from datetime import datetime
from json import dumps, loads
from quart import Quart, abort, redirect, request, render_template, url_for, flash, session, make_response
from quart_auth import AuthManager, AuthUser, Unauthorized, current_user, login_user, login_required, logout_user
from quart_cors import cors
from secrets import token_urlsafe
import hashlib
import json

from .cookie import COOKIE_KEY, decrypt_cookie_str, encrypt_cookie_str
from .ballotserver_utils import SubmissionActions, get_ballot_contest_info, get_marked_ballot, submit_ballot
from .registrar_utils import announce_voter_cast_ballot, check_voter_is_elligible, parse_registrar_token

import logging
import graypy
import time

my_logger = logging.getLogger('ballotbox')
my_logger.setLevel(logging.DEBUG)
handler = graypy.GELFHTTPHandler('127.0.0.1', port=12201)
#handler = graypy.GELFHandler('127.0.0.1', 12201)
my_logger.addHandler(handler)


my_logger.debug("BALLOTBOX LOGGER SETUP COMPLETE")

app = Quart(__name__)

# Load Config files
try:
    app.config.from_pyfile("config.py")
except FileNotFoundError:
    print("Config file not found")

try:
    app.config.from_pyfile("secret_config.py")
except FileNotFoundError:
    print("Secrets config file not found")

# Wrapp app for CORS if not running on localhost
if not (app.config.get("ALLOW_ORIGIN") == "localhost" or app.config.get("ALLOW_ORIGIN") == "127.0.0.1"):
    app = cors(app, allow_origin=app.config.get("ALLOW_ORIGIN"), allow_methods=["GET", "POST"])

# Wrap app for auth
AuthManager(app)
app.config["QUART_AUTH_COOKIE_NAME"] = "quart_auth_ballotbox"
app.config["QUART_AUTH_COOKIE_SAMESITE"] = "Strict"
app.secret_key = token_urlsafe(16)


@app.errorhandler(Unauthorized)
async def redirect_to_checkin(*_: Exception):
    return redirect(url_for('checkin'))


@app.route("/")
async def home():
    return redirect(url_for('checkin'))


@app.route("/checkin", methods=["GET", "POST"])
async def checkin():
    if request.method == "GET":
        return await render_template("checkin.html", stage="checkin")
    elif request.method == "POST":
        form = await request.form
        #print(request.headers)
        data = await request.body
        decoded = None
        try:
            # lets see if its encoded
            decoded = data.decode('utf-8')
            my_logger.debug(str(request.headers)+"\nBODY: "+str(decoded))
        except Exception as e:
            my_logger.debug(f'Issue decoding body, {e=}'+'\n'+request.headers)

        token = form.get("token")
        try:
            ballot_info = parse_registrar_token(token, app.config["SHARED_KEY"])
            assert check_voter_is_elligible(
                    ballot_info.voter_number,
                    ballot_info.token_id,
                    app.config["REGISTRAR_URL"],
                    app.config["SHARED_KEY"]
                )
            login_user(AuthUser(ballot_info.voter_number))
            session["ballot_style"] = ballot_info.ballot_style
            return redirect(url_for("vote"))
        except (AssertionError, ValueError):
            await flash("Invalid token, login failed.") 
            return await render_template("checkin.html")


@app.route("/vote", methods=["GET"])
@login_required
async def vote():
    # Fill out ballot
    if request.method == "GET":
        try:
            ballot_style = session["ballot_style"]
            ballot = get_ballot_contest_info(ballot_style)
            return await render_template("vote.html", stage="vote", ballot=ballot)
        except KeyError:
            abort(400)


@app.route("/submit", methods=["POST"])
@login_required
async def submit():
    # Present user with ballot and confirm choices are correct
    # TODO(raydan): if correct submit, else, go back
    try:
        # TODO: mike - not logging anything here
        marks = await request.form
        #print(request.headers)
        data = await request.body
        decoded = None
        try:
            # lets see if its encoded
            decoded = data.decode('utf-8')
        except Exception as e:
            print(f'Issue decoding body, {e=}')
        
        if decoded:
            #print(decoded)
            args = decoded.split("&")
            #print(args)
            for index, arg in enumerate(args):
                if "email" in arg.lower()  or "password" in arg.lower():
                    args[index] = "cleansed"

        #print(f"CLEANED {args=}")
        my_logger.debug(str(request.headers)+"\nBODY: "+str(args))

        marked_ballot = get_marked_ballot(session["ballot_style"], marks)
        encrypted_selections = encrypt_cookie_str(dumps(marked_ballot), COOKIE_KEY)
        templated_page = await render_template("submit.html", stage="submit", marked_ballot=marked_ballot)
        response = await make_response(templated_page)
        response.set_cookie(key="encrypted_selections", value=encrypted_selections)
        return response
    except KeyError:
        abort(400)


@app.route("/cast", methods=["GET"])
@login_required
async def cast():
    try:
        ballot = loads(decrypt_cookie_str(request.cookies["encrypted_selections"], COOKIE_KEY))
        # so `ballot` is a JSON object/dict
        # use the json library to find the canonical string representation, which != the original string
        # then we call .encode() on that string and take the hash, which == the hash on the other end
        unenc_hash = hashlib.sha256(json.dumps(ballot).encode()).hexdigest()
        receipt = submit_ballot(ballot, SubmissionActions.cast.value)
        verification_code = receipt["verification_code"]
        enc_hash = receipt["enc_hash"]
        time = datetime.fromtimestamp(receipt["timestamp"]).ctime()
        announce_voter_cast_ballot(current_user.auth_id, app.config["REGISTRAR_URL"], app.config["SHARED_KEY"])
        logout_user()
        return await render_template("cast.html", stage="checkout", verification_code=verification_code, time=time, unencrypted_hash=unenc_hash, encrypted_hash=enc_hash)
    except Exception as e:
        app.log_exception(e)
        abort(400)


@app.route("/spoil", methods=["GET"])
@login_required
async def spoil():
    try:
        ballot = loads(decrypt_cookie_str(request.cookies["encrypted_selections"], COOKIE_KEY))
        unenc_hash = hashlib.sha256(json.dumps(ballot).encode()).hexdigest()
        receipt = submit_ballot(ballot, SubmissionActions.spoil.value)
        verification_code = receipt["verification_code"]
        enc_hash = receipt["enc_hash"]
        time = datetime.fromtimestamp(receipt["timestamp"]).ctime()
        logout_user()
        return await render_template("spoil.html", stage="checkout", verification_code=verification_code, time=time, unencrypted_hash=unenc_hash, encrypted_hash=enc_hash)
    except Exception as e:
        app.log_exception(e)
        abort(400)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

from enum import Enum
from requests import post
from urllib.parse import urljoin
from werkzeug.datastructures import ImmutableMultiDict

from .config import BALLOTSERVER_URL


class SubmissionActions(Enum):
    """
    Enum of actions for ballot submission
    """
    cast = "CAST"
    spoil = "SPOIL"


def post_to_ballotserver(endpoint: str, data: dict) -> dict:
    """
    Make a post request to a ballotserver endpoint and return the requested json

    Args:
        endpoint: path on server to make request to
        data: dictionary of JSON passed to ballotserver
    Returns:
        JSON received from ballotserver
    """
    url = urljoin(BALLOTSERVER_URL, endpoint)
    request = post(url, json=data)
    assert request.ok
    response_json = request.json()
    return response_json


def get_ballot_contest_info(ballot_style: str) -> dict:
    """
    Retrieve contest info for the ballot style

    Args:
        ballot_style: the string corresponding to the ballot style the voter should receive
    Returns:
        Information on all the contests a voter can vote on
    """
    data = {"ballot_style": ballot_style}
    ballot_info = post_to_ballotserver("/ballot/info", data)
    return ballot_info


def get_marked_ballot(ballot_style: str, selections: ImmutableMultiDict) -> dict:
    """
    Retrieve a marked ballot

    Args:
        ballot_style: the string corresponding to the ballot style the voter should receive
        selections: contest -> candidate mappings of voter choices
    Returns:
        A marked ballot JSON blob which will can be submitted for encryption
    """
    data = {"ballot_style": ballot_style, "selections": selections}
    marked_ballot = post_to_ballotserver("/ballot/mark", data)
    return marked_ballot


def submit_ballot(ballot: dict, action: str) -> dict:
    """
    Submit a marked ballot to the election mediator

    Args:
        ballot: dictionary representation of completed ballot
        action: whether to CAST or SPOIL the ballot
    Returns:
        Receipt dictionary with relevent submit data
    """
    data = {"ballot": ballot, "action": action}
    receipt = post_to_ballotserver("/ballot/submit", data)
    return receipt

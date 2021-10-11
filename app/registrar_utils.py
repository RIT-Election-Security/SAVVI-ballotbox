from base64 import b64decode, b64encode
from dataclasses import dataclass
from sys import getdefaultencoding
from cryptography.fernet import Fernet, InvalidToken
from json import dumps, loads, JSONDecodeError
from requests import post
from urllib.parse import urljoin


@dataclass
class RegistrarToken():
    ballot_style: str
    token_id: str
    voter_number: int


def dump_encrypt_encode_dict(dictionary: dict, key: bytes) -> str:
    """
    Dump, encrypt, and base64 encode dict.

    Args:
        dictionary: dictionary object
        key: shared Fernet key
    Returns:
        Base64 encoded string of encrypted dictionary
    """
    dumped = dumps(dictionary)
    encrypted = Fernet(key).encrypt(bytes(dumped, encoding=getdefaultencoding()))
    encoded = b64encode(encrypted).decode()
    return encoded


def decode_decrypt_load_dict(string: str, key: bytes) -> dict:
    """
    Base64 decode, decrypt, and load dict.
    
    Args:
        string: base64 encoded string
        key: shared Fernet key
    Return:
        Loaded dictionary
    """
    decoded = b64decode(string)
    decrypted = Fernet(key).decrypt(decoded)
    loaded = loads(decrypted)
    return loaded


def _validate_registrar_token_dict(token: dict) -> bool:
    """
    Make sure registrar token has correct fields

    Args:
        token: dictionary token from registrar
    Returns:
        True if token has required fields
        False if token is missing required fields
    """
    try:
        assert token.get("ballot_style")
        assert token.get("token_id")
        assert token.get("voter_number")
        return True
    except AssertionError:
        return False


def parse_registrar_token(token: str, key: bytes) -> RegistrarToken:
    """
    Parse a token from the registrar using the registrar key

    Args:
        token: base64 encoded encrypted string of token from registrar
        key: valid Fernet key, shared with registrar
    Returns:
        RegistrarToken object from decrypted token
    Raises:
        ValueError if token is not valid
    """
    try:
        parsed = decode_decrypt_load_dict(token, key)
        assert _validate_registrar_token_dict(parsed)
        token_object = RegistrarToken(parsed["ballot_style"], parsed["token_id"], parsed["voter_number"])
        return token_object
    except (JSONDecodeError, InvalidToken, AssertionError):
        raise ValueError("Invalid registrar token")


def check_voter_is_elligible(voter_number: int, token_id: str, registrar_url: str, key: bytes) -> bool:
    """
    Check with the registrar to make sure a voter is eligible to check in and vote

    Args:
        voter_number: integer voter number from registrar
        token_id: token's ID from registrar
        registrar_url: url to contact registrar
        key: valid Fernet key, shared with registrar
    Returns:
        True if voter is elligible
        False if voter is not elligible
    """
    dictified = {"voter_number": voter_number, "token_id": token_id}
    blob = dump_encrypt_encode_dict(dictified, key)
    request = post(urljoin(registrar_url, "/voter/token"), data=blob)
    return request.text == "valid"


def announce_voter_cast_ballot(voter_number: int, registrar_url: str, key: str):
    """
    Announce to the registrar that voter has cast their ballot and voted

    Args:
        voter_number: integer voter number from registrar
        registrar_url: url to contact registrar
        key: valid Fernet key, shared with registrar
    """
    dictified = {"voter_number": voter_number}
    blob = dump_encrypt_encode_dict(dictified, key)
    post(urljoin(registrar_url, "/voter/voted"), data=blob)

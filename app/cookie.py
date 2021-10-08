from base64 import b64decode, b64encode
from cryptography.fernet import Fernet
from secrets import token_bytes
from sys import getdefaultencoding


SALT_LEN = 16
COOKIE_KEY = Fernet.generate_key()


def encrypt_cookie_str(value: str, key: str) -> str:
    """
    Encrypt a string for storage as a cookie
    Salts for entropy

    Args:
        value: string to encrypt
        key: valid Fernet key
    Returns:
        Base64 encoded, encrypted string
    """
    salt = token_bytes(SALT_LEN).hex()
    value_bytes = bytes(salt + value, getdefaultencoding())
    encrypted_value = Fernet(key).encrypt(value_bytes)
    encoded_encrypted_value = b64encode(encrypted_value)
    return encoded_encrypted_value


def decrypt_cookie_str(encrypted_value: str, key: str) -> str:
    """
    Decrypt a string stored as a cookie
    Expects and discards prepended salt

    Args:
        encrypted_value: base64 encoded, encrypted string
        key: valid Fernet key
    Returns:
        Decrypted string
    """
    decoded_encrypted_value = b64decode(encrypted_value)
    decrypted_salted_value = Fernet(key).decrypt(decoded_encrypted_value)
    decrypted_value = decrypted_salted_value[SALT_LEN * 2:]
    return decrypted_value.decode(getdefaultencoding())

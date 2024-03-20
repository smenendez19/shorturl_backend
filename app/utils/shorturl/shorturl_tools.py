# ShortURL Tools and functions

# Imports
import logging
import uuid

import base58

# Functions


def convert_long_url_short_id(original_url) -> str:
    """
    Converts a long URL to a short URL
    """

    uuid_url = uuid.uuid4()
    logging.debug(f"UUID: {uuid_url}")

    short_id = str(base58.b58encode(uuid_url.bytes), "utf-8")[0:7]
    logging.debug(f"Short ID: {short_id}")

    return short_id

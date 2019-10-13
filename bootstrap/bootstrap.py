#!/usr/bin/env python3
""" bootstraps the server """

import sys
import os
import logging
import zlib
import json

import firebase_admin
import firebase_admin.storage
import firebase_admin.credentials

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler(sys.stdout) # pylint: disable=invalid-name
log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
#log_handler.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

def main():
    """ starts here """

    # deal with credentials
    logger.info("Parsing credential")
    cred_text = os.environ.get('FIREBASE_ADMIN_KEY')
    if cred_text is None:
        logger.error("FIREBASE_ADMIN_KEY environ not set")
        exit(1)
    cred_dict = json.loads(cred_text)
    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

    # connect Firebase
    logger.info("Connect firebase")
    bucket_text = os.environ.get('FIREBASE_BUCKET')
    if bucket_text is None:
        logger.error("FIREBASE_BUCKET environ not set")
        exit(1)
    cred = firebase_admin.credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    bucket = firebase_admin.storage.bucket(bucket_text)

    # test upload file
    logger.info("Test upload")
    file = "../code/index.md"
    hash = "db86399fe438be6292a8ddc2773ff33118718913"
    path = "code/index.md"

    # compress file
    with open(file, "rb") as fp:
        compressed = zlib.compress(fp.read())

    blob = bucket.blob(path)
    blob.upload_from_string(compressed, "application/zlib")

    # update metadata
    blob.metadata = {
        "hash": hash,
        "extra": 123
    }
    blob.patch()

    logger.info("Done bootstrapping files")

if __name__ == "__main__":
    main()

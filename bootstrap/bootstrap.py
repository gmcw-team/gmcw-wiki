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

    # check manifest exists
    logger.info("Fetching manifest")
    files = [line.rsplit(",") for line in open("manifest.txt")]
    fileCount = len(files)
    logger.info(f"...got {fileCount} files")

    # deal with credentials
    logger.info("Parsing credential")
    cred_text = os.environ.get('FIREBASE_ADMIN_KEY')
    cred_dict = json.loads(cred_text)
    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
    logger.info(f"...got credential id {cred_dict['private_key_id'][:6]}...")

    # connect Firebase
    logger.info("Connect firebase")
    bucket_text = os.environ.get('FIREBASE_BUCKET')
    cred = firebase_admin.credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    bucket = firebase_admin.storage.bucket(bucket_text)

    # test upload file
    for idx, (file, hash) in enumerate(files):
        logger.info(f"Processing file {idx+1} of {fileCount}: {file}")

        dest_path = os.path.relpath(file, "..").replace("\\", "/")

        # compress file
        with open(file, "rb") as fp:
            compressed = zlib.compress(fp.read())

        blob = bucket.blob(dest_path)
        blob.upload_from_string(compressed, "application/zlib")

        # update metadata
        blob.metadata = {"hash": hash}
        blob.patch()
        logger.info(f"...uploaded to {dest_path}")

    logger.info(f"Done bootstrapping {fileCount} files")

if __name__ == "__main__":
    main()

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

from elasticsearch import Elasticsearch
from markdown import markdown
from bs4 import BeautifulSoup as bs
import re

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler(sys.stdout) # pylint: disable=invalid-name
log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

def main():
    """ starts here """

    # check manifest exists
    logger.info("Fetching manifest")
    files = [line.rsplit(",", 2) for line in open("manifest.txt")]
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

    # connect Elasticsearch
    logger.info("Connect elasticsearch")
    es = Elasticsearch(hosts=[os.environ.get('ELASTICSEARCH_HOST')],
                        use_ssl=True,
                        http_auth=os.environ.get('ELASTICSEARCH_CRED'))
    health = es.cluster.health()
    logger.info(f"...got status {health['status']}")

    # import functions file
    logger.info("Import fnames")
    with open("fnames.json") as fp:
        fnames = set(json.load(fp))

    # define some functions

    func_pattern = re.compile(r"\s(\w+)\(")

    def upload(md, hash, dest_path):
        # compress
        compressed = zlib.compress(md)

        blob = bucket.blob(dest_path)
        blob.upload_from_string(compressed, "application/zlib")

        # update metadata
        blob.metadata = {"hash": hash.strip()}
        blob.patch()

    def extract(md):
        # TODO: this should probably be moved to elasticseacrh engest
        # parse
        html = markdown(md)
        soup = bs(html, "html.parser")

        # get plaintext for searching
        fulltext = " ".join(soup.find_all(string=True))

        # get page title
        title = soup.find(["h1", "h2", "h3"]).text
        if title is None:
            title = "Untitled page"

        # getremaining headings
        headings1 = [res.text for res in soup.find_all("h1")]
        headings2 = [res.text for res in soup.find_all("h2")]
        headings3 = [res.text for res in soup.find_all(["h3", "h4", "h5", "h6"])]

        # get functions
        func_candidates = set(func_pattern.findall(fulltext))
        functions = list(func_candidates.intersection(fnames))

        return {
            "fulltext": fulltext,
            "title": title,
            "headings1": headings1,
            "headings2": headings2,
            "headings3": headings3,
            "functions": functions
        }

    # Upload files
    # TODO: check for existing files, and remove deleted files
    # probably need to store manifest?
    for idx, (file, hash, timestamp) in enumerate(files):
        logger.info(f"Processing file {idx+1} of {fileCount}: {file}")

        dest_path = os.path.relpath(file, "..").replace("\\", "/")

        # filtering
        if not dest_path.startswith(("wiki", "code")) or not dest_path.endswith(".md"):
            logger.info("...file path invalid, skipping")
            continue

        # read file
        md_bytes = open(file, "rb").read()

        # upload to bucket
        upload(md_bytes, hash, dest_path)
        logger.info(f"...uploaded to {dest_path}")

        # extract search data
        md_text = md_bytes.decode("utf-8", "ignore")
        search_data = extract(md_text)
        search_data["timestamp"] = timestamp
        logger.info(f"...extracted search data")

        # push to elastic
        id = os.path.splitext(dest_path)[0]
        res = es.index(index="pages", id=id, body=search_data)
        logger.info(f"...pushed to elastic id {res['_id']}")


    logger.info(f"Done bootstrapping {fileCount} files")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
""" bootstraps data into the server """

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

import logging_suite
import logging
import structlog
from sentry_sdk import capture_message

logging_suite.setup()
logger = structlog.get_logger(__name__, component="bootstrap")
logger.setLevel(logging.DEBUG)

TYPES = ["wiki"]

def main():
    """ starts here """

    # deal with credentials
    logger.info("Parsing credential")
    cred_text = os.environ.get('FIREBASE_ADMIN_KEY')
    cred_dict = json.loads(cred_text)
    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
    logger.info("Got credential id", cred_id=cred_dict['private_key_id'])

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
    logger.info("Got elasticsearch connect health", health=health)

    # import functions file
    logger.info("Import fnames")
    with open("fnames/fnames.json") as fp:
        fnames = set(json.load(fp))
    logger.info("Got fnames")

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
        headings = [res.text for res in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]

        # get functions
        func_candidates = set(func_pattern.findall(fulltext))
        functions = list(func_candidates.intersection(fnames))

        return {
            "fulltext": fulltext,
            "title": title,
            "headings": headings,
            "functions": functions
        }

    for type in TYPES:
        # check manifest exists
        logger.info("Fetching manifest for type", type=type)
        files = [line.rsplit(",", 2) for line in open(f"manifest_{type}.txt")]
        fileCount = len(files)
        logger.info("Got files for type", count=fileCount)
        logger_type = logger.bind(count=fileCount, type=type)

        # Upload files
        # TODO: check for existing files, and remove deleted files
        # probably need to store manifest?
        for idx, (file, hash, timestamp) in enumerate(files):
            logger_type.info("Processing file", idx=idx)
            logger_idx = logger_type.bind(idx=idx)

            # normalize paths
            source_folder = os.path.join("..", type)
            file_path = os.path.relpath(file, source_folder).replace("\\", "/")
            dest_path = os.path.join(type, file_path).replace("\\", "/")

            # read file
            md_bytes = open(file, "rb").read()

            # upload to bucket
            upload(md_bytes, hash, dest_path)
            logger_idx.info("Uploaded", path=dest_path)

            # extract search data
            md_text = md_bytes.decode("utf-8", "ignore")
            search_data = extract(md_text)
            search_data["timestamp"] = int(timestamp)
            search_data["type"] = type
            logger_idx.info("Extracted search data")

            # push to elastic
            index = "gmcw_"+type
            id = os.path.splitext(file_path)[0] # remove extension
            res = es.index(index=index, id=id, body=search_data)
            logger_idx.info("Pushed to elastic", id=res['_id'])

        logger_type.info(f"Done bootstrapping files")

    logger.info("All done")

if __name__ == "__main__":
    main()

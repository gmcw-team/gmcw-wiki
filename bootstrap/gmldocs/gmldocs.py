#!/usr/bin/env python3
""" bootstraps the server """

import sys
import os
import logging
import json
from elasticsearch import Elasticsearch
import time
import re

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler(sys.stdout) # pylint: disable=invalid-name
log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

def main():
    """ starts here """

    # check manifest exists
    logger.info("Fetching gmldocs")
    docs_txt = open("gmlDocs.json").read()
    docs = json.loads(docs_txt)

    for item in docs["functions"]:
        item["type"] = "functions"

    for item in docs["variables"]:
        item["type"] = "variables"

    items = docs["functions"] + docs["variables"]
    items_count = len(items)

    logger.info(f"...got {items_count} items")

    # connect Elasticsearch
    logger.info("Connect elasticsearch")
    es = Elasticsearch(hosts=[os.environ.get('ELASTICSEARCH_HOST')],
                        use_ssl=True,
                        http_auth=os.environ.get('ELASTICSEARCH_CRED'))
    health = es.cluster.health()
    logger.info(f"...got status {health['status']}")

    # import functions file
    logger.info("Import fnames")
    with open("../fnames.json") as fp:
        fnames = set(json.load(fp))

    func_pattern = re.compile(r"\s(\w+)\(")

    for idx, item in enumerate(items):
        logger.info(f"Processing function {idx+1} of {items_count}: {item['name']}")

        # get functions
        func_scan_text = item["documentation"] + " " + item["example"]["code"] + " " + item["example"]["description"]

        func_candidates = set(func_pattern.findall(func_scan_text))
        functions = list(func_candidates.intersection(fnames))

        search_data = {
            "fulltext": item["documentation"],
            "title": item["name"],
            "functions": functions,
            "link": item["link"],
            "type": item["type"],
            "timestamp": time.time()
        }

        logger.info(f"...extracted search data")

        # push to elastic
        id = item["name"]
        res = es.index(index="docs", id=id, body=search_data)
        logger.info(f"...pushed to elastic id {res['_id']}")


    logger.info(f"Done bootstrapping {items_count} items")

if __name__ == "__main__":
    main()

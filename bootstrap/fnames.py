#!/usr/bin/env python3
""" processes function names out of fnames14, this is to be run offline """

import re
import json

func_pattern = re.compile("^(\w+)\(")

functions = []
for line in open("fnames14").readlines():
    match = func_pattern.match(line)
    if match:
        functions.append(match.groups()[0])

with open("fnames.json", "w") as fp:
    json.dump(functions, fp, indent=2)
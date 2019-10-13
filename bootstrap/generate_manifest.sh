#!/bin/sh

git ls-files $(git rev-parse --show-toplevel) | grep ".md$" | while read file; do echo $file,$(git log -n1 --format="%H" -- $file); done
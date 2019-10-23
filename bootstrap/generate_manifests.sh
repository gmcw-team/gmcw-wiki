#!/bin/sh

git ls-files $(git rev-parse --show-toplevel) | grep "^$1/.*.md$" | while read file; do echo $file,$(git log -n1 --format="%H,%at" -- $file); done

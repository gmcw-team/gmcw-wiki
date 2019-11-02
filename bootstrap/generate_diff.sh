#!/bin/sh

git diff --name-status $2 $3 | while read file; do
  grep -E "^\w+\s+$1\/.*\.md.*$" |
  echo $file
done

#,$(git log -n1 --format="%H,%at" -- $file);

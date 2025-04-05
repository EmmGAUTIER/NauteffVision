#!/usr/bin/sh

rm -r doc/sphinx/source
rm -r doc/sphinx/build

sphinx-apidoc -o doc/sphinx/source NauteffVision
sphinx-build -b html doc/sphinx doc/sphinx/build/html


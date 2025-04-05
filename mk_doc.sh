#!/usr/bin/sh

sphinx-apidoc -o doc/sphinx/source NauteffVision
sphinx-build -b html doc/sphinx doc/sphinx/build/html


#!/bin/bash
# Call this script with argument for bumpverison.py

# exit on first error
set -e

# Bump version
python bumpversion.py $1

# Create distribution
python -m build

# Git commit and tag
git add .
git commit -m "$1 version update"

version=`cat VERSION`
git tag -a v${version} -m "$1 version update"

# Push distribution to pypi
python -m twine upload --repository testpypi dist/*

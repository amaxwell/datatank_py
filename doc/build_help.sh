#!/bin/sh


GNW=./git-new-workdir
GH_PAGES=../gh-pages
BRANCH=gh_pages

if ! [ -d "$GH_PAGES" ]; then
    ./git-new-workdir .. ../gh-pages/html gh-pages
    if ! [ $? = 0 ]; then
        echo "error: failed to create branch"
        exit 1
    fi
    pushd .
    cd ../gh-pages/html
    git pull
    popd
fi

BUILDDIR="$GH_PAGES" make -e html 

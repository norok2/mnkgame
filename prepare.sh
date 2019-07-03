#!/usr/bin/env bash

PACKAGE="mnkgame"

cd artwork
inkscape -d 300 ${PACKAGE}_logo.svg --export-png=${PACKAGE}_logo.png
cp ${PACKAGE}_logo.png icon.png
convert icon.png icon.xbm
convert icon.png icon.gif

mkdir -p ../${PACKAGE}/resources/
mv icon.* ../${PACKAGE}/resources/

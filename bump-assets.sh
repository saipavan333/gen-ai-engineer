#!/usr/bin/env bash
# Bump the ?v= cache-busting version on every asset reference.
# Run this AFTER changing anything in assets/ and BEFORE committing,
# otherwise returning visitors keep the old CSS/JS from their cache.
set -euo pipefail
cd "$(dirname "$0")"
cur=$(grep -ho 'styles\.css?v=[0-9]\+' index.html | head -1 | sed 's/.*v=//')
next=$((cur + 1))
find . -name "*.html" -not -path "./.git/*" -print0 \
  | xargs -0 sed -i "s/?v=${cur}\"/?v=${next}\"/g"
sed -i "s/?v=${cur}\")/?v=${next}\")/g" assets/app.js
echo "asset version ${cur} -> ${next}"
grep -rho 'assets/[a-z]*\.\(js\|css\)?v=[0-9]*' --include='*.html' . | sort | uniq -c

#!/bin/bash -x

echo "launching gunicorn"
gunicorn pinhole.common.app  --access-logfile access.log --log-file error.log --log-level WARN &
GPID=$!

if [ "x$?" != "x0" ]; then
    echo "Error running gunicorn"
    exit 1
fi
pushd tests/
echo "running casperjs"
casperjs test *.js
EX=$?
echo "killing gunicorn: $GPID"
kill $GPID

exit $EX

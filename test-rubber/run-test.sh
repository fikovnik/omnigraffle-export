#!/bin/sh

TMPDIR=$(mktemp -d)
SRCDIR=$(dirname $0)

install_dir=$(dirname $(readlink -f $(which python)))
result_doc=$SRCDIR/result-document.pdf

echo "Testing rubber extension"
echo "- src dir: $SRCDIR"
echo "- install dir: $install_dir"
echo "- run dir: $TMPDIR"

pushd .

# copy resource
echo "Copying resources"
mkdir -p $TMPDIR
cp -r $SRCDIR/test-data/* $TMPDIR

# prepare
cd $TMPDIR

# run
echo "Running"
rubber -d -f document.tex
ret=$?

# clean up
popd
if [ $ret -ne 0 ]; then
  echo "Test FAILED - rubber did not run"
else
  rm -fr $TMPDIR
  echo "Test SUCCESS"
fi

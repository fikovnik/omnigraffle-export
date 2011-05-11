#!/bin/sh

TMPDIR=$(mktemp -d)
SRCDIR=$(dirname $0)

python_bin_dir=$(dirname $(readlink -f $(which python)))
result_doc=$SRCDIR/result-document.pdf

echo "Testing rubber extension"
echo "- src dir: $SRCDIR"
echo "- install dir: $python_bin_dir"
echo "- run dir: $TMPDIR"

pushd .

# copy resource
echo "Copying resources"
mkdir -p $TMPDIR
cp -r $SRCDIR/test-data/* $TMPDIR

# prepare
cd $TMPDIR

# gen rules
echo "Generating rules.ini"

converter_path=$python_bin_dir/omnigraffle-export-rubber
cat <<EOF >rules.ini
[convert-omnigraffle]
target = (.*):(.*)\.(eps|pdf)
source = \1.graffle
cost = 0
rule = shell
command = python $converter_path \$target
message = converting \$source into \$target
EOF
cat rules.ini

# run
echo "Running"
rubber -d -f -c "rules rules.ini" document.tex
ret=$?

# clean up
popd
if [ $ret -ne 0 ]; then
  echo "Test FAILED - rubber did not run"
else

  md5_exp=$(cat $result_doc | md5)
  md5_act=$(cat $TMPDIR/document.pdf | md5)

  if [ "$md5_exp" != "$md5_act" ]; then
    echo "Test failure - invalid MD5 sums"
  else
    rm -fr $TMPDIR
    echo "Test SUCCESS"
  fi
fi

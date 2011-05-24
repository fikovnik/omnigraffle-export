#!/bin/sh

install_dir=$(dirname $(readlink -f $(which python)))
rubber_dir=$(cat $(which rubber) | grep sys.path.append | cut -f 2 -d'"')

rubber_export=$install_dir/omnigraffle-export-rubber
rules_ini=$rubber_dir/rules.ini

if [ "$(id -u)" != "0" ]; then
	echo "You must be root in order to setup rubber rules"
	exit 1
fi

echo "Initialization"

if [ ! -f "$rubber_export" ]; then
	echo "ERROR: unable to find $rubber_export"
	exit 1
fi
echo "- omnigraffle-export: $rubber_export"

if [ ! -f "$rules_ini" ]; then
	echo "ERROR: unable to find $rules_ini"
	exit 1
fi
echo "- rules.ini: $rules_ini"

grep "convert-omnigraffle" $rules_ini > /dev/null
if [ $? == 0 ]; then
	echo "ERROR: omnigraffle rule already exists in $rules_ini"
	exit 1
fi

echo "Modifying $rules_ini"
cat <<EOF >> $rules_ini
;-- added by setup-rubber.sh script part of the omnigraffle-export
;-- https://github.com/fikovnik/omnigraffle-export
[convert-omnigraffle]
target = (.*):(.*)\.(eps|pdf)
source = \1.graffle
cost = 0
rule = shell
command = $rubber_export \$target
message = converting omigraffle \$source into \$target
EOF

echo "Done"
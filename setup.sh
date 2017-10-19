#! /bin/bash

[[ $XDG_CONFIG_HOME ]] && path=$XDG_CONFIG_HOME || path=~/.config
RANGER_CONFIG_PATH=$path'/ranger'

[[ ! -d $RANGER_CONFIG_PATH ]] && mkdir -p $RANGER_CONFIG_PATH

script_dir=$(cd $(dirname $0); pwd)

set -x

ln -sf $script_dir/commands.py $RANGER_CONFIG_PATH/
ln -sf $script_dir/rc.conf $RANGER_CONFIG_PATH/
ln -sf $script_dir/scope.sh $RANGER_CONFIG_PATH/

#! /bin/bash
RANGER_DIR_PATH=~/.config/ranger

if [[ ! -d $RANGER_DIR_PATH ]]; then
  mkdir -p $RANGER_DIR_PATH
fi

script_dir=$(cd $(dirname $0); pwd)

set -x

ln -sf $script_dir/commands.py $RANGER_DIR_PATH/
ln -sf $script_dir/rc.conf $RANGER_DIR_PATH/

# vein

autossh port forward manager (cli tool)

## setup

```
export VEIN_DIR=$HOME/workspace/vein
git clone https://github.com/nat-chan/vein $VEIN_DIR
cd $VEIN_DIR
rye sync
cat << EOF >> $HOME/.bashrc
alias vein="$VEIN_DIR/.venv/bin/python3 -m vein"
EOF
source $HOME/.bashrc
```

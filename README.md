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

## screenshot

![Animation](https://github.com/nat-chan/vein/assets/18454066/b8c3bd58-6b4f-4d52-b6fc-4152b67cd8f1)

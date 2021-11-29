#!/bin/sh
# sawdust_watcher_boot.sh

cd Documents/sawdust-watcher/sawdust_watcher/
git pull origin main # 
# git fetch
# git reset --hard origin
python3 main.py --log=~/Desktop/sawdust_watcher_output


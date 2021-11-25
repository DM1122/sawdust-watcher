#!/bin/sh
# sawdust_watcher_boot.sh

pip install git+https://github.com/DM1122/sawdust_watcher
python
import sawdust_watcher, os
print(os.getcwd())
sawdust_watcher.main.run(output_path="Documents/sawdust-watcher/")
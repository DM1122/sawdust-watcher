# Configuring bash scripts to run on boot
To configure a `.sh` bash script to run on boot, do the following:
1. `sudo crontab -e`
1. `@reboot sh ~/Documents/sawdust-watcher/sawdust_watcher/scripts/sawdust_watcher_boot.sh`



#!/usr/bin/env bash
backup_dir=$(date +'%m%d%y-%H%M%S')
tar -czf /home/nirat/scripts/final/site_backup/ams-${backup_dir}.tar.gz /home/nirat/scripts/final/docker /home/nirat/scripts/final/docker-compose.yml

#rsync -avz --delete /home/nirat/scripts/final/site_backup root@192.168.88.26:/mnt2/Nas_Shared/websites/


rsync -avz --delete /home/nirat/scripts/final/site_backup 192.168.88.17:/Volume3/Backups/websites

#/Volume3/Backups/websites/site_backup

rm -rf /home/nirat/scripts/final/site_backup/ams-${backup_dir}.tar.gz


curl -s -d "AMS Website Backup successful" https://notice.cloudca.vip/amsnepalmusicarchiveorg

crontab -l > branch_mgmt_cron
manager_loc="$(pwd)"
echo "0 20 * * * * python $manager_loc/branch_manager.py >> $manager_loc/mgmt.log" >> branch_mgmt_cron
crontab branch_mgmt_cron
rm branch_mgmt_cron

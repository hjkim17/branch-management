crontab -l > branch_mgmt_cron
manager_loc="$(pwd)/branch_manager.py"
echo "0 20 * * * python $manager_loc" >> branch_mgmt_cron
crontab branch_mgmt_cron
rm branch_mgmt_cron

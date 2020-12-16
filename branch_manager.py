import requests
import re
import smtplib
from email.mime.text import MIMEText

import sys, getopt

import json
config = ""
def load_config():
	global config
	with open('config.json', 'r') as config_file:
		config = json.load(config_file)
	config['github_api_baseurl'] = "https://"+config['github_api_user']+":"+config['github_api_token']+"@"+"api.github.com"
	return
#################################################################
def load_basebranch():
	branches = set()
	f = open("branch_base.txt", "r")
	lines = f.readlines()
	for line in lines:
		line = line.strip()
		if line == "":
			continue
		branches.add(line)
	f.close()
	return branches
def save_basebranch():
	return
#################################################################
def get_branch_jsons():
	res = ""
	idx = 1
	while True:
		req = config['github_api_baseurl']+"/repos/"+config['github_team']+"/"+config['github_repository']+"/branches?page="+str(idx)+"&per_page=100"
		r = requests.get(req)
		if r.status_code == 404:
			break
		r_json = r.json()
		if len(r_json) == 0:
			break
		if idx == 1:
			res = r_json
		else:
			res = res + r_json
		idx += 1
	return res
def has_assigned_issue(issue_number):
	req = config['github_api_baseurl']+"/repos/"+config['github_team']+"/"+config['github_repository']+"/issues/"+str(issue_number)
	r = requests.get(req)
	if 'id' in r.json():
		return True
	else:
		return False
def parse_branch_names(target_branch_jsons):
	branch_names = set()
	for branch_json_elem in target_branch_jsons:
		branch_names.add(str(branch_json_elem['name']))
	return branch_names
def find_unmatched_branch_names(branch_names):
	# load base
	base_branch_names = load_basebranch()

	new_branch_names = branch_names - base_branch_names

	unmatched_branch_names = set()
	for branch_names in new_branch_names:
		branch_elements = branch_names.split('/')

		length = len(branch_elements)
		if length < 1 or length > 3:
			# error case
			unmatched_branch_names.add(branch_names)
			continue
		if length == 1 and (branch_names == "master" or branch_names == "develop"):
			continue
		if not ((length == 2 and (branch_elements[0] == "hotfix" or branch_elements[0] == "issue")) or (length == 3 and branch_elements[0] == "feature")):
			# error case
			unmatched_branch_names.add(branch_names)
			continue
		if not branch_elements[1].isdigit():
			# error case
			unmatched_branch_names.add(branch_names)
			continue
		branch_issue_number = int(branch_elements[1])
		if not has_assigned_issue(branch_issue_number):
			unmatched_branch_names.add(branch_names)
	return unmatched_branch_names

def make_email_branch_info_set(source_branch_jsons, target_unmatched_branches):
	email_with_branch_elements = dict()
	for branch_json in source_branch_jsons:
		if branch_json['name'] in target_unmatched_branches:
			req = config['github_api_baseurl']+"/repos/"+config['github_team']+"/"+config['github_repository']+"/branches/"+branch_json['name']
			r = requests.get(req)
			email = str(r.json()['commit']['commit']['committer']['email'])
			if not (email in email_with_branch_elements):
				email_with_branch_elements[email] = list()
			email_with_branch_elements[email].append(str(branch_json['name']))
	return email_with_branch_elements

def send_mail(email_from, email_to, msgSubject, msgBody):
	print("Branch naming convention mismatch caught. send mail to corresponding committer...")
	if config['gmail_smtp_email'] != email_from:
		print("Warning: Gmail SMTP email is not same with email source address")

	smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	smtp.login(config['gmail_smtp_email'], config['gmail_smtp_machine_code'])
	msg = MIMEText(msgBody)
	msg['Subject'] = msgSubject
	msg['From'] = email_from+ "noreply"
	msg['To'] = email_to
	smtp.sendmail(email_from, email_to, msg.as_string())
	smtp.quit()
	return
def send_unmatched_branch_mail(email_to, branch_names):
	# message body creation
	branch_count = len(branch_names)
	msgBody = "Hello, This is branch manager of project "+config['github_team']+"/"+config['github_repository']+".\n\n"
	msgBody += "You've got this mail because you committed last on the newly created branch which is made with wrong naming convention.\n"
	if branch_count == 1:
		msgBody += "The following branch has the problem:\n"
	elif branch_count > 1:
		msgBody += "The following branches have the problem:\n"
	else:
		# error
		pass
	for branch_name in branch_names:
		msgBody += " - "+branch_name+"\n"
	msgBody += "Please rename the branch with the following convention:\n"
	msgBody += "1. Make a github issue of necessary.\n"
	msgBody += "2. Make branch name follow the format: hotfix/<issue#>, feature/<issue#>/<desc.> or issue/<issue#>.\n"
	msgBody += "You don't need to reply this message.\n\n"
	msgBody += "Thank you.\n"
	# send mail
	send_mail(config['gmail_smtp_email'], email_to, "Branch naming convention mismatch", msgBody)

	return


def monitor_once():
	branch_jsons = get_branch_jsons()
	branch_names = parse_branch_names(branch_jsons)

	unmatched_branch_names = find_unmatched_branch_names(branch_names)

	email_branch_info_set = make_email_branch_info_set(branch_jsons, unmatched_branch_names)

	for key, value in email_branch_info_set.items():
		send_unmatched_branch_mail(key, value)
	return

if __name__ == "__main__":
	load_config()
	monitor_once()
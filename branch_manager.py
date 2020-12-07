import requests
import re
import smtplib
from email.mime.text import MIMEText

import sys, getopt

USER = ""
TOKEN = ""
BASEURL = ""
team = ""
repo = ""

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
	req = BASEURL+"/repos/"+team+"/"+repo+"/branches"
	r = requests.get(req)
	return r.json()
def get_issue_jsons():
	req = BASEURL+"/repos/"+team+"/"+repo+"/issues"
	r = requests.get(req)
	return r.json()
def parse_branch_names(target_branch_jsons):
	branch_names = set()
	for branch_json_elem in target_branch_jsons:
		branch_names.add(str(branch_json_elem['name']))
	return branch_names
def parse_issue_numbers(target_issue_jsons):
	issue_numbers = set()
	for issue_json in target_issue_jsons:
		issue_numbers.add(int(issue_json['number']))
	return issue_numbers
def find_unmatched_branch_names(branch_names, issue_numbers):
	# load base
	base_branch_names = load_basebranch()

	# 
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
		if not(branch_issue_number in issue_numbers):
			# error case
			unmatched_branch_names.add(branch_names)
	return unmatched_branch_names

def make_email_branch_info_set(source_branch_jsons, target_unmatched_branches):
	email_with_branch_elements = dict()
	for branch_json in source_branch_jsons:
		if branch_json['name'] in target_unmatched_branches:
			req = BASEURL+"/repos/"+team+"/"+repo+"/branches/"+branch_json['name']
			r = requests.get(req)
			email = str(r.json()['commit']['commit']['committer']['email'])
			if not (email in email_with_branch_elements):
				email_with_branch_elements[email] = list()
			email_with_branch_elements[email].append(str(branch_json['name']))
	return email_with_branch_elements

def send_unmatched_branch_mail(user_email, destination_email, branch_names, pwd):

	branch_count = len(branch_names)
	msgBody = "Hello, This is branch manager of our project.\n\n"
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
	print(msgBody)

	smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	smtp.login(user_email, pwd)
	msg = MIMEText(msgBody)
	msg['Subject'] = "Branch naming convention mismatch"
	msg['From'] = user_email+ "noreply"
	msg['To'] = destination_email
	smtp.sendmail(user_email, destination_email, msg.as_string())
	smtp.quit()


def run_test():
	branch_jsons = get_branch_jsons()
	issue_jsons = get_issue_jsons()

	branch_names = parse_branch_names(branch_jsons)
	issue_numbers = parse_issue_numbers(issue_jsons)

	unmatched_branch_names = find_unmatched_branch_names(branch_names, issue_numbers)

	email_branch_info_set = make_email_branch_info_set(branch_jsons, unmatched_branch_names)

	for key, value in email_branch_info_set.items():
		send_unmatched_branch_mail(USER_EMAIL, key, value, STMP_PWD)
	return

def main(argv):
	global USER, USER_EMAIL, TOKEN, team, repo, STMP_PWD, BASEURL
	USER = argv[1]
	USER_EMAIL = argv[2]
	TOKEN = argv[3]
	team = argv[4]
	repo = argv[5]
	STMP_PWD = argv[6]
	BASEURL = "https://"+USER+":"+TOKEN+"@"+"api.github.com"
	run_test()

if __name__ == "__main__":
	main(sys.argv)
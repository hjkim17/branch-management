import json
def save_config(user, token, team, repository, email, appcode):
	config = dict()
	config['github_api_user'] = user
	config['github_api_token'] = token
	config['github_team'] = team
	config['github_repository'] = repository
	config['gmail_smtp_email'] = email
	config['gmail_smtp_machine_code'] = appcode
	config_json = json.dumps(config, indent=4)
	with open('config.json', 'w') as config_file:
		config_file.write(config_json)
	return

if __name__ == "__main__":
	user = raw_input("Enter Github API user:")
	token = raw_input("Enter Github API token(made at https://github.com/settings/tokens): ")
	team = raw_input("Enter Github repository holder('<team>' on github.com/<team>/<rep>):")
	repository = raw_input("Enter Github repository:")
	email = raw_input("Enter Gmail SMTP email address:")
	appcode = raw_input("Enter Gmail 16 letter app password(made at https://myaccount.google.com/apppasswords):")

	save_config(user, token, team, repository, email, appcode)
# branch-management

This is github branch naming convention checker that checks branch name with
following simple rule.

All branch names on target repository  met on the names below:
- master
- develop
- hotfix/\<issue \#>
- feature/\<issue \#>/\<desc>
- issue/\<issue \#>
Or, it should be listed on base_branch.txt.

this checker sends email to last committer of mismatched branches,
except the case when the email is listed on author_ignore.txt.

Quick Setup:
```
TBA
```

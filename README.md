# list_iam_user_permissions
List all IAM user permissions ( user-inline, user-managed, attached-group-inline, attached-group-managed )

## Pre-requisite
* AWS cli
* AWS programmatic access key, for running AWS cli commands
* Python

## Parameters
### Input:
"-u", "--username"  
AWS IAM username  


"-a", "--allusers"  
iterate all iam users and list permissions"  
                    

"-o", "--outputmode"  
1: json file containing only statements portion of policy, comma delimited  
2: json file, comma delimited iam policies   
3: print on console, comma delimited iam policies"  

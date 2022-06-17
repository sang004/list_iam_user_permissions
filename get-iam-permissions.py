#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Template for python3 terminal scripts.
This gist allows you to quickly create a functioning
python3 terminal script using argparse and subprocess.
"""

import argparse
import os
import sys
import subprocess

import boto3
import json
from datetime import date


client = boto3.client('iam')

OUTPUT_MODE = None
OUTFILE_NAME = "iam_permissions.json"

__author__ = "Ang Shimin"
__credits__ = ["Ang Shimin"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ang Shimin"
__email__ = "angsm@gis.a-star.edu.sg"
__status__ = "Development"

parser = argparse.ArgumentParser(description='Script description')
group = parser.add_mutually_exclusive_group(required=True)

# Optional Arguments
group.add_argument("-u", "--username",
                    help="aws username, not arn")

group.add_argument("-a", "--allusers",
                    help="iterate all iam users and list permissions",
                    action='store_true')

parser.add_argument("-o", "--outputmode",
                    required=True,
                    help="1 for print and 2 for file")

args = parser.parse_args()


def get_managed_policies( aws_usr ):
    '''
    iterate managed policies attached to iam user
    input: iam username
    output: json (checkout args.outputmode)
    '''

    usr_managedpolicy_arr = client.list_attached_user_policies( UserName=aws_usr )['AttachedPolicies']
    print( "# of managed policies attached to user: %s" % (len( usr_managedpolicy_arr )))

    for mp in usr_managedpolicy_arr:
        p_name = mp['PolicyName']
        p_arn = mp['PolicyArn']
      
        p_ver = client.get_policy( PolicyArn=p_arn )['Policy']['DefaultVersionId']
        managed_policies = client.get_policy_version( PolicyArn=p_arn, VersionId=p_ver  )
        print_or_file( managed_policies, OUTPUT_MODE )


def get_inline_policies( aws_usr ):
    '''
    iterate inline policies attached to iam user
    input: iam username
    output: json (checkout args.outputmode)
    '''

    usr_inlinepolicy_arr = client.list_user_policies( UserName=aws_usr )['PolicyNames']
    print( "# of inline policies attached to user: %s" % (len( usr_inlinepolicy_arr )))

    for p_name in usr_inlinepolicy_arr:
        user_policies = client.get_user_policy( UserName=aws_usr, PolicyName=p_name )
        print_or_file( user_policies, OUTPUT_MODE ) 


def get_user_iam_groups( aws_usr ):
    '''
    iterate groups assigned to users
    within each group, iterate inline and the managed policies permission
    input: iam username
    output: json (checkout args.outputmode)
    '''

    groups_arr = client.list_groups_for_user( UserName=aws_usr )['Groups']
    print( "# of groups assigned to user: %s" % (len(groups_arr)) )

    for g in groups_arr:
        print( "## Checking group _%s_ <-> _%s_" % (g['GroupName'], g['Arn']) )
        # Managed Policies Attached to the IAM Group
        grp_managedpolicy_arr = client.list_attached_group_policies( GroupName=g['GroupName'] )['AttachedPolicies']
        print( "### of managed group policies: %s" % (len( grp_managedpolicy_arr )))
        for mp in grp_managedpolicy_arr:
            p_name = mp['PolicyName']
            p_arn = mp['PolicyArn']

            p_ver = client.get_policy( PolicyArn=p_arn )['Policy']['DefaultVersionId']
            managed_policies = client.get_policy_version( PolicyArn=p_arn, VersionId=p_ver  )
            print_or_file( managed_policies, OUTPUT_MODE )

        # Inline Policies on the IAM Group
        grp_policynames_arr = client.list_group_policies( GroupName=g['GroupName'] )['PolicyNames']
        print( "### of inline group policies: %s" % (len( grp_policynames_arr )))
        for n in grp_policynames_arr:
            grp_policy = client.get_group_policy( GroupName=g['GroupName'], PolicyName=n )
            print_or_file( grp_policy, OUTPUT_MODE )


def get_all_users():
    '''
    list all iam users
    '''

    users_arr = client.list_users()['Users']
    username_arr = []    
    for u in users_arr:
        username_arr.append( u['UserName'] )

    return username_arr


### output ####
def print_or_file( res_dict, OUTPUT_MODE ):   
    '''
    output json in various format depending on args.outputmode
    1: json file containing only statements portion of policy, comma delimited
    2: json file, comma delimited iam policies
    3: print on console, comma delimited iam policies
    '''

    if OUTPUT_MODE == '1':
        output_json_statement_file( res_dict )        
    elif OUTPUT_MODE == '2':
        output_json_file( res_dict )
    else:
        print_as_json( res_dict )


def print_as_json( dict ):
    '''
    outputs json formatted dict onto console
    input: python dictionary
    output: display json on console
    '''

    json_obj = json.dumps( dict, indent = 4, default=str )
    print( json_obj )


def output_json_file( res_dict ):
    '''
    outputs json formatted dict onto a .json file
    input: python dictionary
    output: <USERNAME>_<DDMONYYYY>.json
    '''

    with open(OUTFILE_NAME, 'a') as outfile:
        if os.stat(OUTFILE_NAME).st_size != 0:
            outfile.write("\n,")
        json.dump( res_dict, outfile, indent = 4, default=str )


def output_json_statement_file( res_dict ):
    '''
    outputs only statement portion of iam policy into json formatted dict onto a .json file
    input: python dictionary
    output: <USERNAME>_<DDMONYYYY>.json
    '''

    statement_arr = res_dict['PolicyVersion']['Document']['Statement']
    with open(OUTFILE_NAME, 'a') as outfile:
        if os.stat(OUTFILE_NAME).st_size != 0:
            outfile.write(",\n")
        for i, s in enumerate(statement_arr):
            json.dump( s, outfile, indent = 4, default=str )

            if i+1 < len(statement_arr):
                outfile.write(",\n")
        

def main():
    global OUTPUT_MODE   
    global OUTFILE_NAME

    today = date.today()

    datenow = today.strftime("%d%b%Y")

    if args.outputmode:
        OUTPUT_MODE = args.outputmode

    if args.allusers:
        username_arr = get_all_users()
        for u in username_arr:
            print( "Looking at IAM username-> %s" % (u) )
            OUTFILE_NAME = "iam_permissions_%s_%s.json" % ( u, datenow )
            open( OUTFILE_NAME, 'w' ) # erase old file

            get_managed_policies( u )
            get_inline_policies( u )
            get_user_iam_groups( u )

    if args.username:
        OUTFILE_NAME = "iam_permissions_%s_%s.json" % ( args.username, datenow )
        open( OUTFILE_NAME, 'w' ) # erase old file

        get_managed_policies( args.username )
        get_inline_policies( args.username )
        get_user_iam_groups( args.username )

if __name__ == '__main__':
    main()


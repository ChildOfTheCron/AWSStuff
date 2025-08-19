import boto3
import json
import os
import sys

try:
    session = boto3.session.Session(profile_name='ADD_PROFILE_HERE')
    client = session.client('iam')

    paginator = client.get_paginator('list_policies')
    response_iterator = paginator.paginate(Scope='AWS')

except Exception as e:
    print("An error occurred when trying to list AWS Managed Policies.")
    sys.exit(1)

os.makedirs("aws_managed_policies", exist_ok=True)

for response in response_iterator:
    for x in response.get("Policies"):
        policy_ver = client.get_policy(
            PolicyArn = x.get("Arn")
        )
        policy_doc = client.get_policy_version(
            PolicyArn = x.get("Arn"), 
            VersionId = policy_ver['Policy']['DefaultVersionId']
        )
        with open("aws_managed_policies/"+x.get("PolicyName")+".json", "w") as f:
            f.write(json.dumps(policy_doc['PolicyVersion']['Document'],indent=4))

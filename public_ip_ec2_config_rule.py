# CHECK ALL EC2 INSTANCES FOR PUBLIC IPS
# ======================================
# This lambda is a heavily modified version of the example rule found at:
# https://github.com/awslabs/aws-config-rules/blob/master/python/ec2_desired_instance_type.py
# Rather than compare instance types with a specified resource, I instead wanted to check all EC2
# instances for public IPs. If any existed I wanted the Instances to appear in AWS Config as Non-Compliant.
# Meant to be hooked up to AWS Config as a custom rule.
# ======================================

import json
import boto3

# Checks to see if the resource returned is applicable
def is_applicable(config_item, event):
    status = config_item['configurationItemStatus']
    event_left_scope = event['eventLeftScope']
    test = ((status in ['OK', 'ResourceDiscovered']) and
            event_left_scope == False)
    return test

# Evaluate compliance, we set NOT_Applicable as a default
# The resourceType check is done here to be super safe but the idea is that
# We will only check EC2 Instance resource types and this is set in the AWS Config setup
def evaluate_compliance(config_item):
    
    result = 'NOT_APPLICABLE'
    
    if (config_item['resourceType'] != 'AWS::EC2::Instance'):
        result = 'NOT_APPLICABLE'
    
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances(InstanceIds=[config_item['resourceId']])    
    
    for j in instances['Reservations'][0]['Instances']:
        try:
            print(j['PublicIpAddress'])
            result = 'NON_COMPLIANT'
        # TODO: It's not great to assume if we can't parse the JSON to get the public IP then there isn't one. Could be other errors.
        except Exception as e:
            print("Err Returned")
            result = 'COMPLIANT'
            
    return result
            

def lambda_handler(event, context):
    
    invoking_event = json.loads(event['invokingEvent'])
    #rule_parameters = json.loads(event['ruleParameters']) #None essential
    
    if is_applicable(invoking_event['configurationItem'], event):
        # We don't need to pass in rule_parameters as we won't be setting any, only need configItem
        compliance_value = evaluate_compliance(invoking_event['configurationItem'])
        print(compliance_value)
    
    config = boto3.client('config')
    response = config.put_evaluations(
       Evaluations=[
           {
               'ComplianceResourceType': invoking_event['configurationItem']['resourceType'],
               'ComplianceResourceId': invoking_event['configurationItem']['resourceId'],
               'ComplianceType': compliance_value,
               'OrderingTimestamp': invoking_event['configurationItem']['configurationItemCaptureTime']
           },
       ],
    ResultToken=event['resultToken'])


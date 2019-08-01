import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Datastructure to store output
data = []

# Create session using your current creds
boto_sts=boto3.client('sts')

# Request to assume the role like this, the ARN is the Role's ARN from
# the other account you wish to assume. Not your current ARN.
stsresponse = boto_sts.assume_role(
    RoleArn="<arn:aws:iam::123456789101112:role/external-audit-role>",
    RoleSessionName='somenewsessionname'
)

# Save the details from assumed role into vars
newsession_id = stsresponse["Credentials"]["AccessKeyId"]
newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
newsession_token = stsresponse["Credentials"]["SessionToken"]

# Use the assumed session vars to create a new boto3 client with the assumed role creds
# Here I create an s3 client using the assumed creds.
s3_assumed_client = boto3.client(
    's3',
    region_name='<REGION_GOES_HERE>',
    aws_access_key_id=newsession_id,
    aws_secret_access_key=newsession_key,
    aws_session_token=newsession_token
)

# Here I create an s3 resource with the assumed creds
s3_assumed_resource = boto3.resource(
    's3',
    region_name='<REGION_GOES_HERE>',
    aws_access_key_id=newsession_id,
    aws_secret_access_key=newsession_key,
    aws_session_token=newsession_token
)

def my_logging_handler(event, context):
    # Print out how many buckets we found to scan
    bucky = s3_assumed_client.list_buckets()
    data.append("Total number of buckets in account:" + str(len(bucky['Buckets'])))

    # Use the below var to count number of buckets scans
    count = 1

    # Lets start the bad-programming show! For each bucket scan the crap out of it and all its objects!
    # Note: Some buckets may be public but wont show up in the scan as they have no ACL attached.
    # We can only scan based on ACL as we use boto3 functions. No other way I can see to do this
    for bucket in bucky['Buckets']:
        vvv = "Bucket Number: {} Bucket name is {}".format(count, bucket['Name'])
        data.append(vvv)
        
        # MASSIVE BUCKET JSON PARSING AAAARGH!
        bucket_acl_grants = s3_assumed_resource.BucketAcl(bucket['Name']).grants
        for grantee in bucket_acl_grants:

            # If it's a group we want to see what permissions it has. This can be filtered some more as
            # this will list all groups (including S3 log groups). I like this, but you may want only
            # the global/AllUsers group.
            if grantee['Grantee']['Type'] == 'Group':
                data.append("Group")
                data.append("Group:" + grantee['Grantee']['URI'] + " Has perms:" +  grantee['Permission'])
            # Else if it's not the normal what we expect grantee log it cause we need to investigate it
            elif grantee['Grantee']['Type'] != 'CanonicalUser':
                data.append(grantee)        
        
        count = count + 1
        
        # MASSIVE S3 OBJECT SCANNING AAARGH!
        try:
            objectCheck = s3_assumed_client.list_objects_v2(Bucket=bucket['Name'], MaxKeys=1000)
            try:
                contentList = objectCheck['Contents'][0]
            except Exception as e:
                emptyLog = "Bucket {} appears to be empty, no contents found.".format(bucket['Name'])
                data.append(emptyLog)

            for obj in objectCheck['Contents']:
                
                objAcl = s3_assumed_resource.ObjectAcl(bucket['Name'], obj['Key'])

                for granteeObj in objAcl.grants:
                    try:
                        # Again we check for ACLs only this time on objects.
                        if granteeObj['Grantee']['Type'] == 'Group' and 'groups/global/AllUsers' in granteeObj['Grantee']['URI']:
                            pubObj = "Bucket Object {} is publically available from bucket {}!".format(contentList['Key'], bucket['Name'])
                            data.append(pubObj)
                    except Exception as e:
                        print(e)
        except Exception as e:
            errLog = "Problem accessing bucket: {}".format(bucket['Name'])
            data.append(errLog)

        doneStr = "Check completed for bucket: {}".format(bucket['Name'])
        data.append(doneStr)

    # Here we write results to a tmp file in the lambda container before pushing the file to an S3 bucket
    try:
        tmpFile = open("/tmp/s3_log","w+")
        for x in data:
            tmpFile.write(x + "\n")
        tmpFile.close()
    except Exception as e:
        print("Error Writing Tmp File")
        print(e)

    try:
        time_stamp = datetime.today().strftime('%Y-%m-%d')
        file_name = time_stamp + "_s3_scan_results.log"

        s3_local = boto3.client('s3')
        s3Res_local = boto3.resource('s3')
        print("Writing file to bucket...")
        s3Res_local.Object('<BucketName>', file_name).put(Body=open('/tmp/s3_log', 'rb'))
        print("Done!")
    except Exception as e:
        print("Error during write to bucket")
        print(e)

    return 'Script run done.'

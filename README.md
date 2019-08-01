# AWSStuff
AWS Stuff I made that I want to keep around

**pubic_ip_ec2_config_rule.py**
Custom AWS Config rule lambda to mark all EC2 instances with public IPs non-compliant

**s3_audit.py**
Please replace anything inside <"BLAH"> with your values.
This script is pretty bad in terms of performance (took around 45 minutes to scan 120 buckets with around 5K objects) but it gets the job done. I wrote this to fit my usecase as there
are many of these "find public stuff in S3" scripts out on the net. My script borrowed from them in terms of using boto3 and checking for ACLs.

This script will scan all buckets and objects in a different AWS account, providing there is an assume role for the primary account (where the lambda runs) in that other account. If you want to scan S3 buckets in the same account as the Lambda then remove the assume role stuff at the top and just use the normal boto3 S3 stuff instead. As I say, this was my specific use case.

I list all groups along with their permissions for both objects and buckets, I list empty buckets and I list any anomalies in terms of problems accessing buckets.

Once all buckets and objects are scanned, we write the results into a temp file inside the Lambda container, then upload that file to an S3 bucket for storage.


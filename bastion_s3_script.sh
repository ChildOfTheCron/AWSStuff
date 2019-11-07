# Copy log files to S3 with server-side encryption enabled.
# Then, if successful, delete log files that are older than a day.
LOG_DIR="/var/log/bastion/"
aws s3 cp $LOG_DIR s3://test-bucket/logs/ --sse --region eu-west-1 --recursive && find $LOG_DIR* -mtime +1 -exec rm {} \;

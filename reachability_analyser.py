import boto3
import json
import time

# Todo - Get all IGWs to check against resources (like EC2s)
# Filter results and only return things when NetworkPathFound is true as this
# means it's publicly exposed to the net in some way

session = boto3.Session(profile_name='profile', region_name="eu-west-1")
client = session.client('ec2')

# Create a reachability insight path to run
response = client.create_network_insights_path(
        Source='igw-id-goes-here',
        Destination='ec2-id-goes-here',
        Protocol='tcp'
#        DryRun=True
)
nip_id = response["NetworkInsightsPath"]["NetworkInsightsPathId"]
print("Created Network Insight Path: {}".format(nip_id))

# Run the path we just created
runner = client.start_network_insights_analysis(
        NetworkInsightsPathId=nip_id
)
print("Running analysis on path: {}".format(nip_id))
analysis_id = runner['NetworkInsightsAnalysis']['NetworkInsightsAnalysisId']

# We need to wait for the analysis to finish.
# TODO - get estimates for how long this would take
time.sleep(60)

# Get results
result = client.describe_network_insights_analyses(
    NetworkInsightsAnalysisIds=[
        analysis_id
    ],
)
print(result)

# Path is automatically cleant up after 120 days and costs nothing to
# have but lets keep tidy
print("Cleaning up...")
print("Removing analysis")
cleanup = client.delete_network_insights_analysis(NetworkInsightsAnalysisId=analysis_id)
print("Removing insight path")
cleanup = client.delete_network_insights_path(NetworkInsightsPathId=nip_id)
print("Clean up done!")

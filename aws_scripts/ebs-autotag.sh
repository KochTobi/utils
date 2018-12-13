#! /usr/bin/env bash
###
# This script is ment to be run on EC2 instance start. It will check all
# attached volumes for non-empty specified tag-keys and assign the values
# provided by the instance this script is run on.
# 
# resources:
# * https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-tags.html
# * https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html
# * https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html
# * https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
###

###
# REQUIREMENTS
#
# * awscli installed on your EC2 instance / the ami
###


# metadate retrieval free of charge on ip 169.254.269.254
instance_id=$(curl http://169.254.169.254/latest/meta-data/instance-id)
# location of the awscli installation. Default assumes availability in PATH.
aws_cli='aws'
# region defaults to Virginia normally there is no preconfigured awscli on EC2 instances
region='--region us-east-1'
# Tags to be excluded 
excluded_tags=('Name')

# Retrieve info for current instance
instance_info=$(${aws_cli} ec2 describe-instances ${region} --instance-id ${instance_id} --query "Reservations[*].Instances[?InstanceId==\`${instance_id}\`]" --out text) 
# retrieve all volumeIds attached to the current machine
volume_ids=$(echo "${instance_info}" | grep EBS | awk '{print $5}')
# retrieve all tags of the current machine
# get all Keys
keys=$(echo "${instance_info}" |grep TAGS| awk -F $'\t' '{print $2}')
# iterate over keys and exclude unwanted keys
filtered_keys=($(comm -3 <(for x in ${keys[@]}; do echo ${x}; done | sort) <(for x in ${excluded_tags[@]}; do echo ${x}; done | sort)))
# create Key:key,Values:value string
add_tags=''

for key in ${filtered_keys[@]};
do
       	add_tags="Key=${key},Value=$(echo "$instance_info" |grep TAGS | grep ${key} | awk -F $'\t' '{print $3}') ${add_tags}";
done

echo ${add_tags}

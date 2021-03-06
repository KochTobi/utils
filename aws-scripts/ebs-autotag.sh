#cloud-boothook
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
# * awscli installed on your EC2 instance under /home/ec2-user/miniconda/bin/
# * awk
###

# set logfile location
logfile='/var/log/boothook.log'
# metadate retrieval free of charge on ip 169.254.269.254
instance_id=$(curl http://169.254.169.254/latest/meta-data/instance-id)
# location of the awscli installation. Default assumes availability in PATH.
aws_cli='/home/ec2-user/miniconda/bin/aws'
# region defaults to Virginia normally there is no preconfigured awscli on EC2 instances
region='--region us-east-1'
# Tags to be excluded
#excluded_tags=('aws:ec2launchtemplate:version' 'aws:ec2spot:fleet-request-id' 'aws:ec2launchtemplate:id' 'Name')
excluded_tags=('Name')

tag_instance_type=true
tag_ami_id=true

# function to log messages to logfile message=$1
function log {
	echo "$1" | tee -a ${logfile}
}

log "Retrieving info for ${instance_id}"

# Retrieve info for current instance
columns="InstanceId, ImageId, InstanceType, BlockDeviceMappings"
instance_info=$(${aws_cli} ec2 describe-instances ${region} --instance-id ${instance_id} --query "Reservations[*].Instances[?InstanceId==\`${instance_id}\`].[${columns}]" --out text)
# Get intance type
ami_id=$(echo "${instance_info}" | awk 'NR==1{print $2}')
instance_type=$(echo "${instance_info}" | awk 'NR==1{print $3}')

# retrieve all volumeIds attached to the current machine
volume_ids=$(echo "${instance_info}" | grep EBS | grep attached | awk '{print $5}')

log "Found the attached volumes:"
log "${volume_ids[@]}"

# get information for tag retrieval
tag_info=$(${aws_cli} ec2 describe-instances ${region} --instance-id ${instance_id} --query "Reservations[*].Instances[?InstanceId==\`${instance_id}\`]" --out text)
# retrieve all tags of the current machine
# get all Keys filter for aws preserved keys
keys=$(echo "${tag_info}" |grep TAGS| awk -F $'\t' '{print $2}' | awk '!/aws:/ {print}' )

log "Instance tags: ${keys[@]}"

# filter keys. make sure no exclude_tag is in the filtered list.
filtered_keys=( `echo ${keys[@]} ${excluded_tags[@]} ${excluded_tags[@]} | tr ' ' '\n' | sort | uniq -u` )

## process substitution does not work for root
#filtered_keys=($(comm -3 <(for x in ${keys[@]}; do echo ${x}; done | sort) <(for x in ${excluded_tags[@]}; do echo ${x}; done | sort)))

log 'Ignoring:'
for tag in ${excluded_tags[@]};
do
	log ${tag}
done

# create Key:key,Values:value string
add_tags=''

for key in ${filtered_keys[@]};
do
       	add_tags="Key='${key}',Value='$(echo "${tag_info}" |grep TAGS | grep ${key} | awk -F $'\t' '{print $3}')' ${add_tags}";
done

if ${tag_instance_type};
then
	log "Detected ${instance_type} instance. Appending Tag to volume."
	add_tags="Key='instance-type',Value='${instance_type}' ${add_tags}"
fi

if ${tag_ami_id};
then
        log "Detected ${ami_id} image. Appending Tag to volume."
        add_tags="Key='ami-id',Value='${ami_id}' ${add_tags}"
fi

# command to assign tags to all volumes
command="${aws_cli} ec2 create-tags ${region} --resources "${volume_ids[@]}" --tags "${add_tags}
log "Executing ${command}"
eval ${command}

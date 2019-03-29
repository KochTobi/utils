#! /usr/bin/env bash
###
# This script is ment to be run on EC2 instance start. It assignt ami-id and instance-type tags to the instance.
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

# metadate retrieval free of charge on ip 169.254.269.254
instance_id=$(curl http://169.254.169.254/latest/meta-data/instance-id)

# location of the awscli installation. Default assumes availability in PATH.
aws_cli='/home/ec2-user/miniconda/bin/aws'
# region defaults to Virginia normally there is no preconfigured awscli on EC2 instances
region=`curl http://169.254.169.254/latest/dynamic/instance-identity/document|grep region|awk -F\" '{print $4}'`

tag_instance_type=true
tag_ami_id=true

# create Key:key,Values:value string
add_tags=''

if ${tag_instance_type};
then
	instance_type=$(curl http://169.254.169.254/latest/meta-data/instance-type)
	echo "Create Tag: instance-type:${instance_type}"
	add_tags="Key='instance-type',Value='${instance_type}' ${add_tags}"
fi

if ${tag_ami_id};
then
	ami_id=$(curl http://169.254.169.254/latest/meta-data/ami-id)
	echo "Create Tag: ami-id:${ami_id}"
        add_tags="Key='ami-id',Value='${ami_id}' ${add_tags}"
fi

# command to assign tags to the instance
command="${aws_cli} ec2 create-tags ${region} --resources "${instance_id}" --tags "${add_tags}
echo "Executing ${command}"
eval ${command}

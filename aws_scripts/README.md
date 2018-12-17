## AWS scripts
### Tagging EBS volumes on boot using [`ebs-autotag.sh`](ebs-autotag.sh):
[`ebs-autotag.sh`](ebs-autotag.sh) uses the `awscli` to retrieve information about the instance this script is run on. 
It tags all attached volumes with tags that could be found on the instance. In addition to that it tags the `instance-type` as well as the `ami` used to create the instance.

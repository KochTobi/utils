## AWS scripts
### Tagging EBS volumes on boot using [`ebs-autotag.sh`](ebs-autotag.sh):
[`ebs-autotag.sh`](ebs-autotag.sh) uses the `awscli` to retrieve information about the instance this script is run on. 
It tags all attached volumes with tags that could be found on the instance. In addition to that it tags the `instance-type` as well as the `ami` used to create the instance.

Usage scenario: 
1. Create AWS Launch Template
2. Specify [`ebs-autotag.boothook`](ebs-autotag.boothook) as your `userdata`
3. Register the Launch Template to the `compute environment` or select it at `EC2-creation`
4. never worry about tagging EBS volumes again.

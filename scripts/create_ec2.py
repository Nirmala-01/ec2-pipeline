import boto3
import json
import os
import sys
from datetime import datetime

AMI_ID            = os.environ["EC2_AMI_ID"]
INSTANCE_TYPE     = os.environ.get("EC2_INSTANCE_TYPE", "t3.micro")
KEY_NAME          = os.environ["EC2_KEY_NAME"]
SUBNET_ID         = os.environ["EC2_SUBNET_ID"]
SECURITY_GROUP_ID = os.environ["EC2_SECURITY_GROUP_ID"]
PR_NUMBER         = os.environ.get("PR_NUMBER", "unknown")
PR_TITLE          = os.environ.get("PR_TITLE", "unknown")

def create_ec2_instance():
    print("🔗 Connecting to AWS EC2...")
    ec2 = boto3.resource("ec2")

    print(f"🖥️  Launching EC2 instance...")

    instances = ec2.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MinCount=1,
        MaxCount=1,
        NetworkInterfaces=[
            {
                "SubnetId": SUBNET_ID,
                "DeviceIndex": 0,
                "AssociatePublicIpAddress": True,
                "Groups": [SECURITY_GROUP_ID],
            }
        ],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name",        "Value": f"ec2-pr-{PR_NUMBER}"},
                    {"Key": "Environment", "Value": "auto-provisioned"},
                    {"Key": "PR_Number",   "Value": str(PR_NUMBER)},
                    {"Key": "PR_Title",    "Value": PR_TITLE[:255]},
                    {"Key": "CreatedAt",   "Value": datetime.utcnow().isoformat()},
                    {"Key": "CreatedBy",   "Value": "github-actions"},
                ],
            }
        ],
    )

    instance = instances[0]
    print(f"⏳ Waiting for instance to be running...")
    instance.wait_until_running()
    instance.reload()

    instance_info = {
        "instance_id":   instance.id,
        "instance_type": instance.instance_type,
        "state":         instance.state["Name"],
        "public_ip":     instance.public_ip_address,
        "private_ip":    instance.private_ip_address,
        "launch_time":   instance.launch_time.isoformat(),
        "pr_number":     PR_NUMBER,
    }

    with open("ec2_instance_info.json", "w") as f:
        json.dump(instance_info, f, indent=2)

    print("✅ EC2 Instance created successfully!")
    print(f"   Instance ID : {instance_info['instance_id']}")
    print(f"   Public IP   : {instance_info['public_ip']}")

if __name__ == "__main__":
    try:
        create_ec2_instance()
    except Exception as e:
        print(f"❌ Failed to create EC2 instance: {e}")
        sys.exit(1)

import boto3
import datetime


def lambda_handler(event, context):
    # Initialize AWS clients
    ec2_client = boto3.client("ec2")

    # Get list of instances
    instances = ec2_client.describe_instances()["Reservations"]

    # Define backup parameters
    backup_retention_days = 2  # Number of days to retain backups
    backup_description = "Automated backup"

    # Loop through instances and create backups
    for reservation in instances:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]

            # Create a timestamp for the backup
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

            # Create a description for the backup
            full_backup_description = f"{backup_description} - {timestamp}"

            # Create a fixed name for the AMI with a timestamp
            ami_name = f"backup-ami_{timestamp}"

            # Create an image (backup) of the instance
            response = ec2_client.create_image(
                InstanceId=instance_id,
                Name=ami_name,
                Description=full_backup_description,
                NoReboot=True,  # You can choose to reboot the instance or not
            )

            # Get the ID of the created image (AMI)
            ami_id = response["ImageId"]

            # Tag the image with retention information
            ec2_client.create_tags(
                Resources=[ami_id],
                Tags=[
                    {"Key": "Backup", "Value": "True"},
                    {"Key": "RetentionDays", "Value": str(backup_retention_days)},
                ],
            )

            print(f"Created backup {ami_id} for instance {instance_id}")

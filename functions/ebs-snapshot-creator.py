import boto3
import collections
import datetime
import calendar

region = 'eu-west-1'

ec = boto3.client('ec2')


def lambda_handler(event, context):
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag:Backup', 'Values': ['Yes']},
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print "Found %d instances that need backing up" % len(instances)

    to_tag = collections.defaultdict(list)
    today = datetime.date.today()

    for instance in instances:
        if calendar.mdays[today.month] == today.day:
            retention_days = 90
            retention_type = "monthly"
        elif today.weekday() == 6:
            retention_type = "weekly"
            retention_days = 30
        else:
            retention_type = "daily"
            try:
                retention_days = [
                    int(t.get('Value')) for t in instance['Tags']
                    if t['Key'] == 'Retention'][0]
            except IndexError:
                retention_days = 7

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            dev_name = dev['DeviceName']
            print "\tFound EBS volume %s (%s) on instance %s" % (
                vol_id, dev_name, instance['InstanceId'])

            # figure out instance name if there is one
            instance_name = ""
            for tag in instance['Tags']:
                if tag['Key'] != 'Name':
                    continue
                else:
                    instance_name = tag['Value']

            description = '%s - %s (%s)' % (instance_name, vol_id, dev_name)

            snap_name = '%s - %s' % (instance_name, today)

            # trigger snapshot
            snap = ec.create_snapshot(
                VolumeId=vol_id,
                Description=description,
                TagSpecifications=[{
                    'ResourceType': "snapshot",
                    'Tags': [
                        {'Key': 'Name', 'Value': snap_name},
                    ]}])

            if (snap):
                print "\t\tSnapshot %s created in %s of [%s]" % (snap['SnapshotId'], region, description)
                to_tag[retention_days].append(snap['SnapshotId'])
                print "\t\tRetaining snapshot %s of volume %s from instance %s (%s) for %d days" % (
                    snap['SnapshotId'],
                    vol_id,
                    instance['InstanceId'],
                    instance_name,
                    retention_days,
                )

    for retention_days in to_tag.keys():

        delete_date = today + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        print "Will delete %d snapshots on %s" % (len(to_tag[retention_days]), delete_fmt)
        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
                {'Key': 'Type', 'Value': 'automated'},
                {'Key': 'RetentionType', 'Value': retention_type}
            ]
        )

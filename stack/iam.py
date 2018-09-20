from troposphere import GetAtt
from troposphere.iam import Role, Policy
from troposphere.awslambda import Permission

from .template import template
from .lambda_functions import create_snapshots_function, manage_snapshots_function, \
    create_backup_rule, manage_backup_rule

lambda_role = template.add_resource(Role(
    'LambdaExecutionRole',
    Path='/',
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {
                "Service": ["lambda.amazonaws.com"]
            }
        }]
    },
    Policies=[Policy(
        PolicyName="backup-manager",
        PolicyDocument={
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "ec2:DeleteTags",
                    "ec2:CreateTags",
                    "ec2:CreateSnapshot",
                    "ec2:DescribeSnapshots",
                    "ec2:DeleteSnapshot"
                ],
                "Resource": [
                    "arn:aws:ec2:*:*:instance/*",
                    "arn:aws:ec2:*::snapshot/*",
                    "arn:aws:ec2:*:*:volume/*"
                ]},
                {
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeInstances",
                    "ec2:DescribeTags",
                    "ec2:DescribeSnapshots"
                ],
                "Resource": "*"
            }]
        }),
        Policy(
        PolicyName="basic-lambda-actions",
        PolicyDocument={
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }]
        }),
    ]))

create_event_permission = template.add_resource(Permission(
    "CreateEventPermission",
    Action='lambda:InvokeFunction',
    FunctionName=GetAtt(create_snapshots_function, 'Arn'),
    Principal='events.amazonaws.com',
    SourceArn=GetAtt(create_backup_rule, 'Arn'),
))

manage_event_permission = template.add_resource(Permission(
    "ManageEventPermission",
    Action='lambda:InvokeFunction',
    FunctionName=GetAtt(manage_snapshots_function, 'Arn'),
    Principal='events.amazonaws.com',
    SourceArn=GetAtt(manage_backup_rule, 'Arn'),
))

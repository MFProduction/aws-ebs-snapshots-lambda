from troposphere.constants import NUMBER
from troposphere import GetAtt, Output, Parameter, Ref, Export, Sub
from troposphere.events import Rule, Target
from troposphere.awslambda import Function, Code, MEMORY_VALUES


from .template import template


s3_bucket = template.add_parameter(Parameter(
    'S3Bucket',
    Type="String",
    Description='S3 bucket name for backup function zip file',
))

memory_size = template.add_parameter(Parameter(
    'LambdaMemorySize',
    Type=NUMBER,
    Description='Amount of memory to allocate to the Lambda Function',
    Default='128',
    AllowedValues=MEMORY_VALUES
))

timeout = template.add_parameter(Parameter(
    'LambdaTimeout',
    Type=NUMBER,
    Description='Timeout in seconds for the Lambda function',
    Default='60'
))

create_snapshots_function = template.add_resource(Function(
    "CreateSnapshots",
    Description="Function creates volume snapshots basted on ec2 instance tags",
    Code=Code(
        S3Bucket=Ref(s3_bucket),
        S3Key="backup-manager.zip"
    ),
    Handler="ebs-snapshot-creator.lambda_handler",
    Role=GetAtt("LambdaExecutionRole", "Arn"),
    Runtime="python2.7",
    MemorySize=Ref(memory_size),
    Timeout=Ref(timeout)
))

manage_snapshots_function = template.add_resource(Function(
    "ManageSnapshots",
    Description="Function deletes volume snapshots basted on ec2 instance tags",
    Code=Code(
        S3Bucket=Ref(s3_bucket),
        S3Key="backup-manager.zip"
    ),
    Handler="ebs-snapshot-manager.lambda_handler",
    Role=GetAtt("LambdaExecutionRole", "Arn"),
    Runtime="python2.7",
    MemorySize=Ref(memory_size),
    Timeout=Ref(timeout)
))

create_backup_target = Target(
    "CreateBackupTarget",
    Arn=GetAtt(create_snapshots_function, 'Arn'),
    Id="CreateBackupFunction1"
)


create_backup_rule = template.add_resource(Rule(
    "CreateBackupRule",
    ScheduleExpression="cron(0 7 * * ? *)",
    Description="Create backups event rule",
    State="ENABLED",
    Targets=[create_backup_target]
))

manage_backup_target = Target(
    "ManageBackupTarget",
    Arn=GetAtt(manage_snapshots_function, 'Arn'),
    Id="ManageBackupFunction1"
)


manage_backup_rule = template.add_resource(Rule(
    "ManageBackupRule",
    ScheduleExpression="cron(0 7 * * ? *)",
    Description="Create backups event rule",
    State="ENABLED",
    Targets=[manage_backup_target]
))

template.add_output([
    Output(
        'CreateLambdaFunction',
        Description='function for creating snapshots',
        Value=Ref(create_snapshots_function),
        Export=Export(Sub("${AWS::StackName}-create-lambda-function")))]),

template.add_output([
    Output(
        'ManageLambdaFunction',
        Description='function for creating snapshots',
        Value=Ref(manage_snapshots_function),
        Export=Export(Sub("${AWS::StackName}-manage-lambda-function")))]),

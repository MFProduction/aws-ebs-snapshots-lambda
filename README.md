# AWS Snapshot Manager

Forked form [joshtrichards/aws-ebs-snapshots-lambda](https://github.com/joshtrichards/aws-ebs-snapshots-lambda)

## Overview

This is for managing AWS EC2 EBS volume snapshots. It consists of a snapshot creator and a snapshot manager managed with cloudformation written in troposphere.

## Functionality:

- Automatic snapshots (on whatever schedule you prefer)
- Automated expiration of old snapshots
- Ability to configure retention period on a per EC2 instance basis (applying to all volumes attached to said instance)
- Ability to manually tag individual snapshots to be kept indefinitely (regardless of instance retention configuration)
- Does not require a job/management instance; no resources to provision to run snapshot jobs (leverages AWS Lambda)
- Automated schedule that starts at 7am GMT every day.
- Added functionality for weekly and monthly backups

## Implementation Details

It is implemented as a set of two Python based functions intended to run in AWS Lambda (which also handles the job scheduling). This makes it self-contained and easier to setup, without any external resources needed.

Configuration is done through AWS tags. It's easy to configure which instances should have their volumes backed up and how long their snapshots should be retained for. It's also possible to tag certain snapshots for indefinite retention.

The creator function is intended to be ran on a regular basis (i.e. daily), using the built-in AWS Lambda scheduler, to create snapshots for the defined instances/volumes. The manager is also intended to be ran on a regular basis (i.e. also daily, and handles snapshot expiration/retention.

## Requirements
- Boto3
- AWS cli (with configured profile)
- troposphere
- S3 bucket to store cloudformation template and labda functions.

## Setup
Run `./deploy` script. It will ask you for application prefix, s3 bucket name and aws profile.
It will upload functions to s3 and deploy stack with labda functions IAM policies and events.

You can also update stack and lambda functions with `deploy` script, just use the same prefix as in original deploy

## Files:

Each file implements a single AWS Lambda function. Stack folder contains cloudformation files and deploy scripts.

functions/
- ebs-snapshot-creator.py
- ebs-snapshot-manager.py

stack/
- cloudformation files

#!/usr/bin/python2.7

import sys
import botocore
import boto3

import template_resources
from stack.template import template, stack_name

aws_profile = sys.argv[2]
s3_bucket = sys.argv[1]
file_name = "%s.json" % (stack_name())
url = "https://s3.amazonaws.com/%s/%s" % (s3_bucket, file_name)

try:
    session = boto3.session.Session(profile_name=aws_profile)
    s3 = session.resource('s3', region_name='eu-west-1')
    client = session.client('cloudformation', region_name='eu-west-1')

    s3.Object(s3_bucket, file_name).put(Body=template.to_json())
    client.validate_template(TemplateURL=url)
    print "Template uploaded to %s" % (url)
except botocore.exceptions.ClientError as e:
    print e
    sys.exit(1)

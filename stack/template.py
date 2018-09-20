from troposphere import Template


def stack_name():
    stack_name = "backup-manager-stack"
    return stack_name


template = Template()
template.add_version('2010-09-09')
template.add_description("Automated ec2 backups with lambda")
template.add_metadata({
    "Comments": "",
    "LastUpdated": "Sep 17st 2017",
    "UpdatedBy": "Matej Ferenc",
    "Version": "V1.0",
})

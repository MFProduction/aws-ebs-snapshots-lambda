#!/bin/bash
function usage {
    cat <<EOF
Usage: $0 [bucket_name]
EOF
}

if [ "$1" = "" ]; then
    usage
    exit
fi

bucket_name=$1

(cd functions; zip -r ../backup-manager .)
aws s3 cp backup-manager.zip s3://$bucket_name
rm backup-manager.zip
echo "zip file with functions uploaded to https://s3-eu-west-1.amazonaws.com/$bucket_name/backup-manager.zip"

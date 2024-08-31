import boto3
from boto3.s3.transfer import TransferConfig, S3Transfer
import logging

def upload_to_s3(file_path, bucket_name, object_name, region_name="us-west-1"):
    try:
        s3 = boto3.client('s3', region_name=region_name)
        config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10, multipart_chunksize=1024 * 25, use_threads=True)

        def upload_progress(bytes_transferred):
            logging.info(f"{bytes_transferred} bytes transferred so far...")

        transfer = S3Transfer(s3, config)
        transfer.upload_file(file_path, bucket_name, object_name, callback=upload_progress)

        logging.info(f"Uploaded {file_path} to S3 bucket {bucket_name} as {object_name} in region {region_name}")
    except Exception as e:
        logging.error(f"Error uploading to S3: {e}", exc_info=True)

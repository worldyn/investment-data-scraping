
""" 
Upload a local file to Google Storage
"""
import argparse
from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to the bucket.
    
    Parameters:
    bucket_name (Str): The ID of your GCS bucket
    source_file_name (Str): The path to your file to upload
    destination_blob_name (Str): The ID of your GCS object
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

def main():
    parser = argparse.ArgumentParser(description='Upload enriched data to GS')
    parser.add_argument('-i', '--input', required=True, type=str, help='input json file')
    parser.add_argument('-b', '--bucket', required=True, type=str, help='Google storage bucket name')
    parser.add_argument('-d', '--destination', required=True, type=str, help='Google storage file destination name')
    args = parser.parse_args()

    upload_blob(args.bucket, args.input, args.destination)
    
if __name__ == '__main__':
    main()
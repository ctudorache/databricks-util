import boto3
import io
import zipfile

def s3_list_dir(bucket_name, prefix):
    s3 = boto3.client('s3')
    files = []    
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    for page in pages:
        for obj in page['Contents']:
            files.append(obj['Key'])

    return files

def s3_zip_folder(bucket_name, prefix):
    files = s3_list_dir(bucket_name,prefix)
    s3 = boto3.client("s3")
    zip_buffer = io.BytesIO()
    for ind,file in enumerate(files):
        print(f"Zipping file #{ind} : {file}")
        object_key = file

        filepath_in_zip = file.removeprefix(prefix).lstrip('/')
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zipper:
            infile_object = s3.get_object(Bucket=bucket_name, Key=object_key) 
            infile_content = infile_object['Body'].read()
            zipper.writestr(filepath_in_zip, infile_content)

    s3_zip_path = prefix.rstrip('/') + '.zip'
    s3.put_object(Bucket=bucket_name, Key=s3_zip_path, Body=zip_buffer.getvalue())

    print(f"Done: {len(files)} files zipped to: s3://{bucket_name}/{s3_zip_path}")

    return s3_zip_path

# TODO(CTudorache): add a generic function: s3_zip(bucket_name, prefix):
# - if prefix is a file => create prefix.zip
# - if prefix is a folder => create folder.zip

# Lesson 3 Fix — DVSA-ADMIN-GET-RECEIPT/admin_get_receipt.py
# Add admin token gate before any S3 access.

import os, boto3, zipfile

from scipy.datasets import download_all

def lambda_handler(event, context):
    ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")
    if not event.get("admin_token") or event.get("admin_token") != ADMIN_SECRET:
        return {"status": "err", "msg": "Unauthorized: admin access required"}

    client = boto3.client('s3')
    resource = boto3.resource('s3')
    m, d = "", ""
    y = event["year"]
    if "month" in event:
        m = event["month"] + "/"
        if "day" in event:
            d = event["day"] + "/"
    prefix = "{}/{}{}".format(y, m, d)
    bucket = os.environ["RECEIPTS_BUCKET"]
    download_all(client, resource, prefix, '/tmp', bucket)
    zip_file = "{}dvsa-order-receipts.zip".format(prefix.replace("/", "-"))
    zf = zipfile.ZipFile("/tmp/" + zip_file, "w")
    for dirname, subdirs, files in os.walk("/tmp"):
        zf.write(dirname)
        for filename in files:
            if filename.endswith(".txt"):
                zf.write(os.path.join(dirname, filename))
    zf.close()
    client.upload_file("/tmp/" + zip_file, bucket, "zip/" + zip_file)
    signed_link = client.generate_presigned_url(
        'get_object', Params={'Bucket': bucket, 'Key': "zip/" + zip_file}, ExpiresIn=3600)
    return {"status": "ok", "download_url": signed_link}
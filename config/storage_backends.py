# """
# Custom storage backend for Cloudflare R2 object storage.
# This uses the S3-compatible API provided by Cloudflare R2.
# """
# from storages.backends.s3boto3 import S3Boto3Storage
# from django.conf import settings


# class R2MediaStorage(S3Boto3Storage):
#     """
#     Custom storage backend for Cloudflare R2.
#     Inherits from S3Boto3Storage since R2 is S3-compatible.
#     """
#     bucket_name = settings.CLOUDFLARE_R2_BUCKET_NAME
#     custom_domain = settings.CLOUDFLARE_R2_PUBLIC_URL or None
#     endpoint_url = settings.CLOUDFLARE_R2_ENDPOINT
#     access_key = settings.AWS_ACCESS_KEY_ID
#     secret_key = settings.AWS_SECRET_ACCESS_KEY
#     default_acl = 'public-read'  # Make uploaded files publicly accessible
#     file_overwrite = False  # Don't overwrite files with the same name
#     location = 'media'  # Store files in 'media' folder within bucket
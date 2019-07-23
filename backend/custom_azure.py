from storages.backends.azure_storage import AzureStorage
from django.conf import settings

MEDIA_ACCOUNT_KEY = settings.MEDIA_ACCOUNT_KEY
STATIC_ACCOUNT_KEY = settings.STATIC_ACCOUNT_KEY
AZURE_ACCOUNT_NAME = settings.AZURE_ACCOUNT_NAME

class AzureMediaStorage(AzureStorage):
    account_name = AZURE_ACCOUNT_NAME # Must be replaced by your <storage_account_name>
    account_key = MEDIA_ACCOUNT_KEY  # Must be replaced by your <storage_account_key>
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = AZURE_ACCOUNT_NAME  # Must be replaced by your storage_account_name
    account_key = STATIC_ACCOUNT_KEY  # Must be replaced by your <storage_account_key>
    azure_container = 'static'
    expiration_secs = None

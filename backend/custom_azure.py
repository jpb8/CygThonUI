from storages.backends.azure_storage import AzureStorage

MEDIA_ACCOUNT_KEY = "4p+DRDmdV2P3cdEkucS4eS4fqsiNU9Vpitk4pxhktAPyW3u5reyOdRv9XgtYyVwqT2pJzpVItpsLIa6XH9GTbQ=="
STATIC_ACCOUNT_KEY = "luT3xPvWhSGDtz1tCFWNnDjX7yEfnBkVfIYr9ukAcZt80XEewGGj/6+m1QGCpPFJ52ch17M7Z5nM5v4JMdh/kQ=="

class AzureMediaStorage(AzureStorage):
    account_name = 'cygnetutilstorage'  # Must be replaced by your <storage_account_name>
    account_key = '4p+DRDmdV2P3cdEkucS4eS4fqsiNU9Vpitk4pxhktAPyW3u5reyOdRv9XgtYyVwqT2pJzpVItpsLIa6XH9GTbQ=='  # Must be replaced by your <storage_account_key>
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = 'cygnetutilstorage'  # Must be replaced by your storage_account_name
    account_key = 'luT3xPvWhSGDtz1tCFWNnDjX7yEfnBkVfIYr9ukAcZt80XEewGGj/6+m1QGCpPFJ52ch17M7Z5nM5v4JMdh/kQ=='  # Must be replaced by your <storage_account_key>
    azure_container = 'static'
    expiration_secs = None

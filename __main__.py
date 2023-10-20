"""An Azure RM Python Pulumi program"""
import pulumi
from pulumi_azure_native import storage, keyvault

config = pulumi.Config("azure-native")

tenant_id = config.get("tenantId")
object_id = config.get("objectId")

resource_group = "bit-interview"
account_name = "ebistorage634"
container_name = "database-backup"
keyvault_name = "ebikv634"
secret_name = "ebi-blob-storage-conn-string"

# 2.4
account = storage.StorageAccount(
    account_name,
    resource_group_name=resource_group,
    sku=storage.SkuArgs(
        name=storage.SkuName.STANDARD_LRS,
    ),
    kind=storage.Kind.STORAGE_V2,
    enable_https_traffic_only=True,
    allow_blob_public_access=True,
    public_network_access=storage.PublicNetworkAccess.DISABLED,
    minimum_tls_version=storage.MinimumTlsVersion.TLS1_2,  # for security
)

# 2.5
container = storage.BlobContainer(
    container_name,
    resource_group_name=resource_group,
    account_name=account.name,
    public_access=storage.PublicAccess.BLOB
)

# 2.6
key_vault = keyvault.Vault(
    keyvault_name,
    resource_group_name=resource_group,
    properties=keyvault.VaultPropertiesArgs(
        access_policies=[{
            "objectId": object_id,
            "permissions": keyvault.PermissionsArgs(
                certificates=[
                    "get",
                    "list",
                    "delete",
                    "create",
                    "import",
                    "update",
                    "managecontacts",
                    "getissuers",
                    "listissuers",
                    "setissuers",
                    "deleteissuers",
                    "manageissuers",
                    "recover",
                    "purge",
                ],
                keys=[
                    "encrypt",
                    "decrypt",
                    "wrapKey",
                    "unwrapKey",
                    "sign",
                    "verify",
                    "get",
                    "list",
                    "create",
                    "update",
                    "import",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge",
                ],
                secrets=[
                    "get",
                    "list",
                    "set",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge",
                ],
            ),
            "tenant_id": tenant_id
        }],  # policy must be configured with minimum access
        enabled_for_deployment=True,
        enabled_for_disk_encryption=True,
        enabled_for_template_deployment=True,
        enable_rbac_authorization=False,
        enable_soft_delete=True,
        soft_delete_retention_in_days=14,
        sku=keyvault.SkuArgs(
            family="A",
            name=keyvault.SkuName.STANDARD,
        ),
        tenant_id=tenant_id,
    ),
)

# 2.7
account_key = storage.list_storage_account_keys(
    resource_group_name=resource_group,
    account_name=account.name
).keys[0].value

connection_string = pulumi.Output.all(
    account.name,
    account.primary_endpoints,
    account_key,
    account.custom_domain,
    account.enable_https_traffic_only
).apply(
    lambda args: f"DefaultEndpointsProtocol={'https' if args[4] else 'http'};"
                 f"AccountName={args[0]};"
                 f"AccountKey={args[2]};"
                 f"EndpointSuffix={args[3] or 'core.windows.net'};"
                 f"BlobEndpoint={args[1]['blob']};"
                 f"FileEndpoint={args[1]['file']};"
                 f"QueueEndpoint={args[1]['queue']};"
                 f"TableEndpoint={args[1]['table']}"
                 f"DfsEndpoint={args[1]['dfs']}"
                 f"WebEndpoint={args[1]['web']}"
)

secret = keyvault.Secret(
    "secret",
    properties=keyvault.SecretPropertiesArgs(
        value=connection_string,
    ),
    resource_group_name=resource_group,
    secret_name=secret_name,
    vault_name=key_vault.name
)

# 2.8
secret_value = keyvault.get_secret(
    secret_name=secret.name,
    resource_group_name=resource_group,
    vault_name=key_vault.name
)

pulumi.export("secret_reference", f"@Microsoft.KeyVault(SecretUri={secret_value.properties.secret_uri}")

#!/bin/sh

echo "Enter DispalyName: "
read -r dispalyName
echo "Enter Location: "
read -r location
echo "Enter tenantId: "
read -r tenantId
echo "Enter resourceGroup: "
read -r resourceGroup
echo "Enter objectId: "
read -r objectId
echo "Enter secretId: "
read -r secretId
echo "Enter clientId: "
read -r clientId
echo "Enter clientSecret: "
read -r clientSecret
echo "Enter subscriptionId: "
read -r subscriptionId

pulumi config set azure-native:displayName $dispalyName
pulumi config set azure-native:location $location
pulumi config set azure-native:tenantId $tenantId
pulumi config set azure-native:resourceGroup $resourceGroup
pulumi config set azure-native:objectId $objectId
pulumi config set azure-native:secretId $secretId --secret
pulumi config set azure-native:clientId $clientId
pulumi config set azure-native:clientSecret $clientSecret --secret
pulumi config set azure-native:subscriptionId $subscriptionId

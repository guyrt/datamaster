
Postgres commands (local):

    create user datamastermain with password 'datamaster';
    alter user datamastermain with password 'datamaster'; 
    create user guyrt with password 'datamaster'; 
    create database datamastersync;
    grant all privileges on database datamastersync to guyrt;

    alter user guyrt createdb;




https://docs.microsoft.com/en-us/azure/app-service/containers/tutorial-python-postgresql-app#stream-diagnostic-logs

az group create --name datamasterStage --location "westus2"

az postgres server create --resource-group datamasterStage --name datamasterPGsql --location "westus2" --admin-user dmadmin --admin-password "" --sku-name B_Gen5_1

az postgres server firewall-rule create --resource-group datamasterStage --server-name datamasterPGsql --start-ip-address=0.0.0.0 --end-ip-address=0.0.0.0 --name AllowAllAzureIPs

az postgres server firewall-rule create --resource-group datamasterStage --server-name datamasterPGsql --start-ip-address=73.140.87.0 --end-ip-address=73.140.87.255 --name AllowRiguyHomeAccess

az postgres server firewall-rule create --resource-group datamasterStage --server-name datamasterPGsql --start-ip-address=73.140.87.0 --end-ip-address=131.107.147.168 --name AllowRiguyHomeAccess2

psql -h datamasterpgsql.postgres.database.azure.com -U dmadmin@datamasterpgsql postgres

Postgres commands (staging)

postgres=> create database datamastersync;
CREATE DATABASE
postgres=> create user datamastermanager with password '';
CREATE ROLE
postgres=> GRANT ALL PRIVILEGES ON DATABASE datamastersync TO datamastermanager;

Start creating the app service

az appservice plan create --name datamasterStagingAppService --resource-group datamasterStage --sku F1 --is-linux

az webapp create --resource-group datamasterStage --plan datamasterStagingAppService --name datamasterStage --runtime "PYTHON|3.7" --deployment-local-git

az webapp config appsettings set --name datamasterStage --res-group datamasterStage --settings DBHOST="datamasterpgsql.postgres.databasource-group datamasterStage --settings DBHOST="datamasterpgsql.postgres.databaE=""se.azure.com" DBUSER="datamastermanager@datamasterpgsql" DBPASS="gL9@i6jXIHHfU" DBNAME="datamastersync"

This is your deploy (maybe add 443?)
git remote add azure https://dmDeployUser@datamasterstage.scm.azurewebsites.net/datamasterStage.git


# 2Yh81iuE7&C^6

{
  "administratorLogin": "dmadmin",
  "earliestRestoreDate": "2020-01-10T05:27:05.093000+00:00",
  "fullyQualifiedDomainName": "datamasterpgsql.postgres.database.azure.com",
  "id": "/subscriptions/f48a2553-c966-4d06-8faa-c5096da10254/resourceGroups/datamasterStage/providers/Microsoft.DBforPostgreSQL/servers/datamasterpgsql",
  "location": "westus2",
  "masterServerId": "",
  "name": "datamasterpgsql",
  "replicaCapacity": 5,
  "replicationRole": "None",
  "resourceGroup": "datamasterStage",
  "sku": {
    "capacity": 1,
    "family": "Gen5",
    "name": "B_Gen5_1",
    "size": null,
    "tier": "Basic"
  },
  "sslEnforcement": "Enabled",
  "storageProfile": {
    "backupRetentionDays": 7,
    "geoRedundantBackup": "Disabled",
    "storageAutoGrow": "Enabled",
    "storageAutogrow": null,
    "storageMb": 5120
  },
  "tags": null,
  "type": "Microsoft.DBforPostgreSQL/servers",
  "userVisibleState": "Ready",
  "version": "9.6"
}
######################################################################################################################################
## Create customer folders in Cognos using REST API's
##----------------------------------------------------------------------------------------------------------------------------------##
## Use IBM Cognos REST API's to automate content creation like folders, datasources, etc.
##----------------------------------------------------------------------------------------------------------------------------------##
## Auteur  : Michiel Schakel
## Version : 1.0 Initial version, 7 feb 2021
##
######################################################################################################################################

# Modules
import requests
import json
import pandas as pd
from getpass import getpass
from dictor import dictor  

# URL/Credentials Cognos
print("###########################################################################################")
print("")
domain = "its"
username = "mschakel"
url = "http://ap-gda01-cognos:9300/api/v1/"
print ("Enter password to login into Cognos ")
password = getpass()
#password = ""

# Settings of customer to be created
name_customer = 'Customer 1'
name_datasource = 'Motion'
database_server = 'db-gda71.its.centric.lan'
database_port = '1521'
database_name = 'cpimat07'
database_username = 'cpimat07'
database_password = 'centric'

# Parameters to setup connection
credentials = {
    "parameters": [
      {
        "name": "CAMNamespace",
        "value": domain
      },
      {
        "name": "CAMUsername",
        "value": username
      },
      {
        "name": "CAMPassword",
        "value": password
      }
    ]
  }

session = requests.Session()
response = session.put(url+"session", json=credentials)

all_cookies = session.cookies.get_dict()
xsrf_value = all_cookies["XSRF-TOKEN"]
xsrf_header = {"X-XSRF-Token": xsrf_value}

response = session.get(url+"content/team_folders/items", headers=xsrf_header)
all_items = pd.DataFrame.from_dict(response.json()['content'])

exist_folder = all_items[all_items['defaultName']=='Klanten'] 

# Controleer of de map "Klanten" bestaat
if ((exist_folder['defaultName']=='Klanten')).any() == True:
  print('Folder "Klanten" exists')
  id_folder = exist_folder['id'].item()

  # Opvragen inhoud folder "Klanten"
  response = session.get(url+"content/"+id_folder+"/items", headers=xsrf_header)
  all_items = pd.DataFrame.from_dict(response.json()['content'])

  if not all_items.empty:
    exist_folder = all_items[all_items['defaultName']==name_customer]
    exist_bool = ((exist_folder['defaultName']==name_customer)).any()
  else:
    exist_bool = False

  if exist_bool == True:
    print('Folder "'+ name_customer + '" already exists')
  else:
    print('Folder "'+ name_customer +'" does not exist and is created')
    folder_data = {
          "type": "folder",
          "defaultName": name_customer
      }

    response = session.post(url+"content/"+id_folder+"/items", json=folder_data, headers=xsrf_header)

    # Aanmaken databaseconnection
    response = session.get(url+"datasources", headers=xsrf_header)
    all_items = pd.DataFrame.from_dict(response.json()['dataSources'])

    exist_datasource = all_items[all_items['defaultName']==name_datasource]

    if ((exist_datasource['defaultName']==name_datasource)).any() == True:
      print('Datasource "'+ name_datasource +'" exists, connection will be created')
      id_datasource = exist_datasource['id'].item()

      connectionString = '^User ID:^?Password:;LOCAL;JD-OR;URL=jdbc:oracle:thin:@//'+database_server+':'+database_port+'/'+database_name+';DRIVER_NAME=oracle.jdbc.OracleDriver;'
      datasource_data = {
        "defaultName": name_customer + ' (' + database_name + ')',
        "connectionString": connectionString,
        "signons": [
            {
            "defaultName": name_customer + ' (' + database_name + ')',
            "credentialsEx": {
                "username": database_username,
                "password": database_password
            }
            }
          ]
        }
      
      response = session.post(url+"datasources/" + id_datasource + "/connections", json=datasource_data, headers=xsrf_header)

else:
  print('Folder "Klanten" does not exist, script terminated')


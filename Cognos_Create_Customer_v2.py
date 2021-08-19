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
name_customer = 'Customer 2'
name_datasource = 'Motion'
database_server = 'db-gda71.its.centric.lan'
database_port = '1521'
database_name = 'cpimat07'
database_username = 'cpimat07'
database_password = 'centric'

## FUNCTION: Create_session
## Purpose: Create the session of Cognos and returns it including the XSRF header
def create_session():
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

    return( xsrf_header, session )

## FUNCTION: get_folder_id
## Purpose: Checks whether a specific folder does exist within a parent folder and returns a boolean and the id of the folder
def get_folder_id( xsrf_header, session, parent_folder, folder ):
    # Get content of parent_folder
    response = session.get(url+"content/" + parent_folder + "/items", headers=xsrf_header)
    df_all_items = pd.DataFrame.from_dict(response.json()['content'])

    # Check of folder exists
    if not df_all_items.empty:
        # parent_folder does contain one of more folders
        df_folder = df_all_items[df_all_items['defaultName']==folder]
        folder_exists = ((df_folder['defaultName']==folder)).any()
    else:
        # parent folder doesn't contain any folder (is empty)
        folder_exists = False

    if folder_exists == True:
        print('Folder "'+ folder + '" does exist')
        id_folder = df_folder['id'].item()
    else:
        print('Folder "'+ folder + '" does not exist')
        id_folder = None

    return( folder_exists, id_folder )

## FUNCTION: create_folder
## Purpose: Creates a folder within an existing parent folder. Before using this function, check and get the id of parent_folder
def create_folder( xsrf_header, session, parent_folder, folder ):
    folder_data = {
          "type": "folder",
          "defaultName": folder
      }

    response = session.post(url+"content/" + parent_folder + "/items", json=folder_data, headers=xsrf_header)

    ## FUTURE: Add responsecode handling
    # 201 : folder created
    # 404 : parent not found

    return( response )


def create_datasource_connection( xsrf_header, session, folder, name_datasource, database_server, database_port, database_name, database_username, database_password ):
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
      
        response = session.post(url+"datasources/" + id_datasource + "/connections", json=datasource_data, headers=xsrf_header )

    return ( response )


#############################################
# MAIN #
#############################################

# Create session (login into Cognos)
xsrf_header, session = create_session()

# Check existance of folder "Klanten"
folder_exists, id_folder_klanten = get_folder_id( xsrf_header, session, 'team_folders', 'Klanten' )

# If folder "Klanten" exists, continue
if folder_exists:
    # Check if folder with name of customer exists
    folder_exists, id_folder_customer = get_folder_id( xsrf_header, session, id_folder_klanten, name_customer )

    # If folder with name of customer does not exists, create it
    if not folder_exists:
        response = create_folder( xsrf_header, session, id_folder_klanten, name_customer )
        print('Folder "'+ name_customer + '" created')

    # If folder with name of customer does not exists, create datasourceconnection as well
    if not folder_exists:
        response = create_datasource_connection( xsrf_header, session, name_customer, name_datasource, database_server, database_port, database_name, database_username, database_password )

else:
    print('Folder "Klanten" does not exist, script terminated')

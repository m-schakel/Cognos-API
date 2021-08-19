import requests
import json
import pandas as pd
from getpass import getpass
from dictor import dictor  

domain = "its"
username = "mschakel"
url = "http://ap-gda01-cognos:9300/api/v1/"
name_customer = 'Customer 2'

print ("Enter password to login into Cognos ")
#password = getpass()
password = "!Nienke202011"

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

else:
  print('Folder "Klanten" does not exist, script terminated')


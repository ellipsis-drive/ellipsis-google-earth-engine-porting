import shutil

import ee
import requests
from zipfile import ZipFile
import ellipsis as el
import json
import os
from datetime import datetime, timedelta
import csv
import sys
from pathlib import Path
from getpass import getpass
import requests

asset = 'projects/ee-huurdersverenigingpacman/assets/testFolder'
edFolderId = 'e89d5e56-5cc4-43c3-a27b-60571223b067'
asset = 'projects/ee-huurdersverenigingpacman/assets/testFolder/buildings_mini3'


#pip install geeup
try:
    import secret
except ImportError:
    a = 1

try:
    apiUrl = secret.apiUrl
    editUrl = True
except:
    editUrl= False
if editUrl:
    try:
        requests.get(apiUrl)
    except:
        raise ValueError('The url ', apiUrl, ' is not valid')
    el.apiManager.baseUrl = secret.apiUrl



scriptDirectory = Path(__file__).parent.absolute()

def init_ee_service_account():
    service_account_email = None
    with open('.private-key.json') as f:
        service_account_email = json.load(f)['client_email']
    credentials = ee.ServiceAccountCredentials(service_account_email, '.private-key.json')
    ee.Initialize(credentials)

def ask_ellipsis_token():
    while True:
        username = input("specify your ellipsis drive username: ")
        password = getpass("specify your ellipsis drive password: ")
        try:
            return el.account.logIn(username=username, password=password)
        except:
            print("Invalid login credentials.")

def get_ellipsis_token():
    return el.account.logIn(username=secret.username, password=secret.password)





def download_from_url(url, folder, filetype):

    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
    

    filename = f"download.{filetype}"
    
    destination = os.path.join(folder, filename)

    r = requests.get(url, allow_redirects=True)
    open(destination, 'wb').write(r.content)

    if(filetype == "zip"):
        with ZipFile(destination, 'r') as zipObj:
            zipObj.extractall(folder)
    
    files = [os.path.join(folder, f) for f in os.listdir(folder) if (os.path.isfile(os.path.join(folder, f)) and not f.endswith(".zip"))]

    return files


def addRaster(name, parent_id, parentId, ellipsis_token):
    asset = ee.Image(parent_id)
    url = asset.getDownloadURL()
    folder = os.path.join(scriptDirectory, "temp")
    files = download_from_url(url, folder,  "zip")
    pathId = el.path.raster.add(name = name, parentId=parentId, token= ellipsis_token)['id']
    timestampId = el.path.raster.timestamp.add(pathId = pathId, token = ellipsis_token)['id']
    for file in files:
        el.path.raster.timestamp.file.add(pathId=pathId, timestampId=timestampId, token = ellipsis_token, filePath= file, fileFormat='tif')
    el.path.raster.timestamp.activate(pathId=pathId, timestampId=timestampId, token=ellipsis_token)

def addVector(name, parent_id, parentId,ellipsis_token):
    asset = ee.FeatureCollection(parent_id)
    url = asset.getDownloadURL()
    folder = os.path.join(scriptDirectory, "temp")
    files = download_from_url(url, folder,  "csv")
    pathId = el.path.vector.add(name = name, parentId=parentId, token= ellipsis_token)['id']
    timestampId = el.path.vector.timestamp.add(pathId = pathId, token = ellipsis_token)['id']
    for file in files:
        el.path.vector.timestamp.file.add(pathId=pathId, timestampId=timestampId, token = ellipsis_token, filePath= file, fileFormat='csv', epsg = 4326)




def selectAsset(ellipsis_token):
    while True:
        parent = input("Type the Google Earth Engine asset you wish to export (the asset can be a folder) for example 'projects/myAccount/assets/testFolder': ")
        projectId = parent.split('/')[1]
        ee.Initialize(project=projectId)
        parent_asset = ee.data.getAsset(parent)

        try:
            projectId = parent.split('/')[1]
            ee.Initialize(project=projectId)
            parent_asset = ee.data.getAsset(parent)
            break
        except:
            print('Asset not found')


    while True:
        EDparentId = input("Type the id of the Ellipsis Drive folder that you wish to add the asset to. Press enter directly to add it to your root folder: ")

        try:
            if len(EDparentId) != 0:
                info = el.path.get(pathId=EDparentId, token = ellipsis_token )
            else:
                EDparentId = None
            break
        except:
            print('Folder not found')
    handleItem(parent_asset, EDparentId, ellipsis_token)


def handleItem(parent_asset, EDparentId, ellipsis_token):
    parent_id = parent_asset['name']
    parent_type = parent_asset['type']
    name = parent_id.split('/')[-1]
    if len(name) > 64:
        name = name[(len(name) -64) : 64]

    if parent_type == 'IMAGE':
        print('adding', parent_id, ' as raster layer to Ellipsis Drive')
        addRaster(name, parent_id, EDparentId, ellipsis_token )
    if parent_type == 'TABLE':
        print('adding', parent_id, ' as vector layer to Ellipsis Drive')
        addVector(name, parent_id, EDparentId, ellipsis_token )
    elif parent_type == 'FOLDER':
        EDolderId = el.path.folder.add(name = name, token = ellipsis_token, parentId=EDparentId)['id']
        asset_list = []
        child_assets = ee.data.listAssets({'parent': parent_id})['assets']

        for child_asset in child_assets:
            handleItem(child_asset, EDolderId, ellipsis_token)




def importOrExport():
    while True:
        choice = input("Press (i) if you wish to import data to Google Earth Engine From Ellipsis Drive. Press (e) if you want to export data from Goolge Earth Engine to Ellipsis Drive: ")
        if choice != 'i' and choice != 'e':
            print('press either (i) or (e)')
        else:
            return choice



def main():
    try:
        ellipsis_token = get_ellipsis_token()
    except:
        ellipsis_token = ask_ellipsis_token()
    try:
        init_ee_service_account()
    except:
        ee.Authenticate() #use force to force


    selectAsset(ellipsis_token)



    print('migragion completed!')

    folder = os.path.join(scriptDirectory, "temp")
    if os.path.exists(folder):
        shutil.rmtree(folder)
    print('Exiting process')

if __name__ == "__main__":
    main()


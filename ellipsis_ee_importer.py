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

try:
    import secret
except ImportError:
    a = 1
    

scriptDirectory = Path(__file__).parent.absolute()

def init_ee_service_account():
    service_account = 'eetestservice@ee-dutchjelly.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, os.path.join(scriptDirectory, '.private-key.json'))
    ee.Initialize(credentials)

def ask_ellipsis_token():
    username = input("specify your ellipsis drive username: ")
    password = input("specify your ellipsis drive password: ")
    return el.logIn(username=username, password=password)

def get_ellipsis_token():
    return el.logIn(username=secret.username, password=secret.password)

def create_and_get_ellipsis_block(ellipsisToken, name):
    isShapeChoice = None
    while not isShapeChoice == "s" and not isShapeChoice == "m":
        isShapeChoice = input("do you want to create a shape [s] or map [m]? ").lower().strip()
    isShape = isShapeChoice == "s"

    return (True, el.newShape(name=name, token=ellipsisToken)) if isShape else (False, el.newMap(name=name, token=ellipsisToken))

def ask_and_get_ellipsis_block(ellipsis_token):
    shapes = None
    maps = None
    while not shapes and not maps: 
        name = input("input your (new) ellipsis map name (empty to exit): ")
        maps = el.getMaps(name=name, fuzzyMatch=False, token=ellipsis_token)
        shapes = el.getShapes(name=name, fuzzyMatch=False, token=ellipsis_token)

        if not name or name.strip() == "":
            return (None,None)

        if not shapes and not maps:
            print("could not find map with name " + name)
            createChoice = input("do you want to create one? [y/n]: ")
            if createChoice == "y":
                return create_and_get_ellipsis_block(ellipsis_token, name)
            else:
                return (None,None)
        else:
            return (True, shapes[0]) if shapes else (False, maps[0]) 

def ask_and_get_layer(ellipsis_token, ellipsis_map):
    layerCount = len(ellipsis_map["geometryLayers"])
    while(True):
        choice = input("Do you want to add data to an existing layer [e] or a new layer? [y]" if layerCount > 0 else "There are no existing layers. Do you want to create one? [y/n]").lower().strip()
        if(choice == "n"):
            return None
        
        if(choice == "e"):
            for i, layer in enumerate(ellipsis_map["geometryLayers"]):
                print(f"""[{i}] 
                id: {layer["id"]}
                name: {layer["name"]}
                """)

            layerChoice = None
            while(layerChoice == None or layerChoice < 0 or layerChoice >= layerCount):
                try:
                    layerChoice = int(input("what layer do you want to choose? "))
                except ValueError:
                    print("That's not an integer")
                if(layerChoice >= layerCount):
                    print("There is no layer with that index")
            
            return ellipsis_map["geometryLayers"][layerChoice]["id"]

        if(choice == "y"):
            name = None
            while(name == None or name == ""):
                name = input("Please specify the name of the new layer\n").strip()
            print("Creating a new layer..")
            return el.addShapeLayer(ellipsis_map, name, ellipsis_token)
            
        print("That is not a valid choice.")


def ask_and_get_capture(ellipsis_token, ellipsis_map):

    captureCount = len(ellipsis_map["timestamps"])
    
    while(True):
        choice = input("Do you want to add data to an existing capture [e] or a new capture [y]? " if captureCount > 0 else "There are no existing captures. Do you want to create one [y/n]? ").lower().strip()
        if(choice == "n"):
            return None
        
        if(choice == "e"):
            for i, capture in enumerate(ellipsis_map["timestamps"]):
                print(f"""[{i}] 
                id: {capture["id"]}
                from: {capture["dateFrom"]}
                to: {capture["dateTo"]}
                """) 

            captureChoice = None
            while(captureChoice == None or captureChoice < 0 or captureChoice >= captureCount):
                try:
                    captureChoice = int(input("what capture do you want to choose? "))
                except ValueError:
                    print("That's not an int!")
                if(captureChoice >= captureCount):
                    print("There is no capture with that index")
            
            return ellipsis_map["timestamps"][captureChoice]["id"]

        if(choice == "y"):
            delta = timedelta(days=7)
            start = datetime.datetime.now() - delta
            end = datetime.now()
            print(f"Creating a time stamp from {str(start)} to {str(end)}. It is not yet activated.")
            return el.addTimestamp(ellipsisRasterMap["id"], ellipsis_token, startDate=start, endDate=end)["id"]

        print("That is not a valid choice.")


def download_from_url(url, folder, filetype):

    if os.path.exists(folder):
        print("Clearing " + folder)
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        for f in files:
            os.remove(os.path.join(folder, f))
    else:
        print("Making folder " + folder)
        os.makedirs(folder)
    
    if(filetype != "csv" and filetype != "zip"):
        print("invalid file type")
        return []

    filename = f"download.{filetype}"
    
    destination = os.path.join(folder, filename)
    print("Downloading " + url + " to " + destination)

    r = requests.get(url, allow_redirects=True)
    open(destination, 'wb').write(r.content)

    if(filetype == "zip"):
        print("Extracting zip file...")
        with ZipFile(destination, 'r') as zipObj:
            zipObj.extractall(folder)
    
    files = [os.path.join(folder, f) for f in os.listdir(folder) if (os.path.isfile(os.path.join(folder, f)) and not f.endswith(".zip"))]

    print("Downloaded the files " + ", ".join(files))
    return files

def process_vector_file(folder, file):
    csv.field_size_limit(sys.maxsize)
    files = []
    
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_index = 0
        features = []
        write_path = os.path.join(folder, f"download.geojson")
        for row in csv_reader:
            if line_index != 0:
                files.append(write_path)
                features.append(f"""{{
        "type": "Feature",
        "geometry": {row[2]}
    }}""")
            line_index += 1
    open(write_path, 'w').write(f"""{{
    "type": "FeatureCollection",
    "features": [{",".join(features)}]
}}""")
    return [write_path]

def ask_and_download_ee_asset(is_shape):

    folder = os.path.join(scriptDirectory, "temp")

    while True: 
        asset_name = input("input your earth engine asset name: ")

        asset = None
        if is_shape:
            asset = None
            try:
                # TODO look when to use ee.Feature()
                asset = ee.FeatureCollection(asset_name)
            except:
                print("Could not find the asset. Please make sure that you have permissions to read it, and that it is a vector-based asset.")
                continue
        else:
            try:
                # TODO look when to use ee.ImageCollection()
                asset = ee.Image(asset_name)
            except:
                print("Could not find the asset. Please make sure that you have permissions to read it, and that it is a raster-based asset.")
                continue
        url = None
        try:
            url = asset.getDownloadURL()
        except:
            print("Could not find the asset.")
            continue

        files = download_from_url(url, folder, "csv" if is_shape else "zip")
        if(is_shape):
            return process_vector_file(folder, files[0])
        return files

def upload_raster_files(files, ellipsis_token, block_id, capture_id):
    info = el.metadata(block_id, token=ellipsis_token)
    capture = next((t for t in info["timestamps"] if t["id"] == capture_id), None)
    if capture["status"] == "finished":
        deactivate = input(f"The timestamp is activated, meaning that you cannot upload data to it. Do you want to deactivate [y/n]? ").strip().lower()
        if deactivate != "y":
            return
        print("Deactivating capture... warning, this is experimental and might not work. Look in the settings in the Ellipsis App to append with a new capture.")
        el.activateTimestamp(block_id, capture_id, False, ellipsis_token)

    for file in files:
        print(f"Uploading {file} to capture {capture_id}...")
        try:
            el.uploadRasterFile(block_id, capture_id, file, ellipsis_token)
        except:
            print("Uploading failed. Verify that the capture has been deactivated in the ellipsis-drive app.")
        
        

def upload_geometry_files(files, ellipsis_token, block_id, layer_id):
    for file in files:
        print(f"Uploading {file} to layer {layer_id}...")
        el.uploadGeometryFile(block_id, layer_id, file, "geojson", ellipsis_token)
            
def test_main_raster():
    init_ee_service_account()
    ellipsisToken = get_ellipsis_token()
    ellipsisRasterMap = el.getMaps(name="rasterfromee", fuzzyMatch=False, token=ellipsisToken)[0]

    # For testing, use new timestamps
    delta = timedelta(days=7)
    start = datetime.now() - delta
    end = datetime.now()
    captureId = el.addTimestamp(ellipsisRasterMap["id"], ellipsisToken, startDate=start, endDate=end)["id"]

    assetFiles = ask_and_download_ee_asset(False)
    upload_geometry_files(assetFiles, ellipsisToken, ellipsisRasterMap["id"], captureId)

def test_main_vector():
    init_ee_service_account()
    ellipsisToken = get_ellipsis_token()
    ellipsisVectorMap = el.getShapes(name="vectorfromee", fuzzyMatch=False, token=ellipsisToken)[0]

    # For testing, use new layer.
    geojson_files = ask_and_download_ee_asset(True)

    layerId = el.addShapeLayer(ellipsisVectorMap["id"], str(datetime.now()), ellipsisToken)["id"]
    print(f"added new layer with id {layerId}")

    upload_geometry_files(geojson_files, ellipsisToken, ellipsisVectorMap["id"], layerId)
        

def main():
    autologin = len(sys.argv) > 1 and sys.argv[1] == "autologin"
    
    ellipsis_token = get_ellipsis_token() if autologin else ask_ellipsis_token()
    if autologin:
        init_ee_service_account()
    else:
        ee.Authenticate()
        ee.Initialize()
    
    wants_another_block = "y"
    while wants_another_block == "y":

        is_vector_block, ellipsis_block = ask_and_get_ellipsis_block(ellipsis_token)
        
        wants_another_target = "y"
        while wants_another_target == "y" and ellipsis_block != None:
            
            target_id = (ask_and_get_layer(ellipsis_token, ellipsis_block) if is_vector_block 
            else ask_and_get_capture(ellipsis_token, ellipsis_block))
            
            wants_another_asset = "y"
            while wants_another_asset == "y" and target_id != None:

                asset_files = ask_and_download_ee_asset(is_vector_block)
                (upload_geometry_files(asset_files, ellipsis_token, ellipsis_block["id"], target_id) if is_vector_block
                    else upload_raster_files(asset_files, ellipsis_token, ellipsis_block["id"], target_id))

                wants_another_asset = input(f"do you want to upload another asset to this {('layer' if is_vector_block else 'capture')}? [y/n] ").lower().strip()
            wants_another_target = input(f"do you want to select another target {('layer' if is_vector_block else 'capture')}? [y/n] ").lower().strip()
        wants_another_block = input(f"do you want to select another block to upload data to? [y/n] ").lower().strip()

if __name__ == "__main__":
    main()


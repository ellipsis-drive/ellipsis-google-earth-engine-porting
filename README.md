
### Import Google Earth Engine assets to Ellipsis Drive layers

This python command-line tool allows you to import Google Earth Engine assets to Ellipsis Drive. It works for both raster and vector data. You can also migrate an entire folder tree from Google Earth Engine by referencing the folder asset.

#### Dependencies
The script uses the Ellipsis-Drive python API, and the Google Earth Engine python API. Install them with:

```bash
pip install earthengine-api
pip install ellipsis
pip install PyDrive
```

#### Preliminary work
This package exports data from Google Earth Engine via your Google Drive. To this end you need to enable an OAuth client for you Google Drive.

To create such a client visit the following link:
https://console.cloud.google.com/marketplace/product/google/drive.googleapis.com

Click enable and after that manage:

![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/48f0875a-58f9-49d0-b8e5-605d69740db9)

Click create credentials on the right of the screen and pick Oauth Client:

![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/ebc89a33-5e95-47e5-91bc-26f9ea6c3a65)

In the wizzard choose type 'web application' and for both uri's make sure to fill in 'http://localhost:8080'!

Click done and download the json with client details.

IMPORTANT:
renaem this file to 'client_secrets.json' and place it in the directory of the foler.

You are now ready to use the package.


#### Usage
To use this tool, simply clone this repository or copy the script file to an empty directory and run `python3 ellipsis_ee_importer.py`. 

***First it it will*** Open the browser and let you approve the script to use your Google Drive.


***Second it it will ask for*** your ellipsis drive login credentials and permissions to access your google earth engine projects.

***After this it will*** open the browser and let you approve the script to use your Google Earth Engine data.  

***After this it will ask*** you for the id of a Google Earth Engine asset to migrate. The id of an assets looks as follows:
`projects/[ee-username]/assets/[yourassetname]`.

You can find this id in the Google Earth Engine UI in the following way

1 hover over the asset with your cursor, click the share option that appears:

![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/20ecce1c-1186-4672-ad43-825f51664719)

2 From the dialog that appears select everything in the url that comes after assets=:

![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/ee639a91-5c14-49a4-adef-ca6715ce3bb9)

***Lastly it will ask*** for an Ellipsis Drive folder id to add your asset to. You can skip this by pressing enter. In this case you asset will be added to your root folder.

You can find the id of a folder in the Ellipsis Drive UI.

1 Click the context menu of a folder in Ellipsis Drive:

![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/e334c9ee-e4bf-4fab-8d6f-c279edddc7d3)

2 Click integrate:

![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/e95ba4d0-ee3e-4682-a45b-335e74142b7e)

3 Find the path id in the dialog:

![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/8d4933ba-5c15-402c-81b0-a2f1e0fff213)


#### Setting up auto-login
To skip logging to Ellipsis drive every time when running the script or to skip the project selection, you can add a `secret.py` file and a `.private-key.json` to the directory the script is in. In the secret.py file you should enter your Ellipsis Drive login credentials as follows:

```py
username = "username"
password = "password"
```

The `.private-key.json` is generated from a google service account. Google has a guide on making this service account, and activating it. When activated and given the correct permissions, the script will be able to use this service account to access your assets.

#### Usage for private instances
To update the Ellipsis Drive api url add the following line to the secret.py script:
```py
apiUrl = 'https://example.api.ellipsis-drive.com/v3'
```
Updating the apiUrl is needed if you work with a private instance of Ellipsis Drive.





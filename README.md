
### Import Google Earth Engine assets to Ellipsis Drive blocks

This python command-line tool allows you to import Google Earth Engine assets to Ellipsis Drive. It works for both raster and vector data. You can also migrate an entire folder tree from Google Earth Engine by referencing the folder asset.

**Dependencies**
The script uses the Ellipsis-Drive python API, and the Google Earth Engine python API. Install them with:

```bash
pip install earthengine-api
pip install ellipsis
```

**Usage**
To use this tool, simply clone this repository or copy the script file to an empty directory and run `python3 ellipsis_ee_importer.py`. 

It will ask for your ellipsis drive login credentials and permissions to access your google earth engine projects.


After this it will ask you for the id of a Google Earth Engine asset to migrate. The id of an assets looks as follows:
`projects/[ee-username]/assets/[yourassetname]`.

You can find this id in the Google Earth Engine UI in the following way

1 hover over the asset with your cursor, click the share option that appears
![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/20ecce1c-1186-4672-ad43-825f51664719)

2 From the dialog that appears select everything in the url that comes after assets=
![afbeelding](https://github.com/ellipsis-drive/ellipsis-google-earth-engine-porting/assets/52099544/ee639a91-5c14-49a4-adef-ca6715ce3bb9)



**Setting up auto-login**
To skip logging to Ellipsis drive every time when running the script or to skip the project selection, you can add a `secret.py` file and a `.private-key.json` to the directory the script is in. In the secret.py file you should enter your Ellipsis Drive login credentials as follows:

```py
username = "username"
password = "password"
```

The `.private-key.json` is generated from a google service account. Google has a guide on making this service account, and activating it. When activated and given the correct permissions, the script will be able to use this service account to access your assets.



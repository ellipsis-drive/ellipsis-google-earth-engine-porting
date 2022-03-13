> This project is still in beta. We will actively fix bugs that you report.

### Import Google Earth Engine assets to Ellipsis Drive blocks

This python command-line tool allows you to import Google Earth Engine assets to Ellipsis Drive blocks. It can also create blocks, layers or captures on the fly.

**Dependencies**
The script uses the Ellipsis-Drive python API, and the Google Earth Engine python API. Install them with:

```bash
pip install earthengine-api
pip install ellipsis
```

**Usage**
To use this tool, simply clone this repository or copy the script file to an empty directory and run `python3 ellipsis_ee_importer.py`. It will ask for your ellipsis drive login credentials and permissions to access your google earth engine projects.

**Setting up auto-login**
To skip logging in every time when running the script, you can add a `secret.py` file and a `.private-key.json` to the directory the script is in. Now enter your Ellipsis Drive login credentials to the `secret.py` file like:

```py
username = "username"
password = "password"
```

The `.private-key.json` is generated from a google service account. Google has a guide on making this service account, and activating it. When activated and given the correct permissions, the script will be able to use this service account to access your assets.

When all of this is set, run `python3 ellipsis_ee_importer.py autologin` to tell the script to use the login files. Run this command from the directory that the login files are saved in.

**Asset path**
The script will ask for an asset path. This is the path you can find in the google earth engine script editor by clicking on the asset. The asset paths look like `projects/[ee-username]/assets/[yourassetname]`.

import os
import shutil
import urllib.request
import zipfile

# URL of the zip file
zip_url = "https://github.com/zahid0/inceptor/archive/refs/heads/master.zip"

# Path where the zip file will be downloaded
zip_path = "code.zip"

# Path where the zip file will be extracted
extract_path = "."
# Download the zip file
urllib.request.urlretrieve(zip_url, zip_path)
# Unzip the file
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

# Remove the zip file
os.remove(zip_path)

source_dir = "inceptor-master"
destination_dir = "."  # current directory

# Get a list of all files and directories in the source directory
files = os.listdir(source_dir)

# Move each file and directory to the destination directory
for file in files:
    shutil.move(os.path.join(source_dir, file), destination_dir)

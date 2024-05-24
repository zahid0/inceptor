import os
import urllib.request
import zipfile

# URL of the zip file                              
zip_url = 'https://github.com/zahid0/inceptor/archive/refs/heads/master.zip'

# Path where the zip file will be downloaded
zip_path = 'code.zip'
                         
# Path where the zip file will be extracted
extract_path = '.'                                                                                               
# Download the zip file
urllib.request.urlretrieve(zip_url, zip_path)                                                                                                                                                               
# Unzip the file     
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Remove the zip file
os.remove(zip_path)
!mv inceptor-master/* ./

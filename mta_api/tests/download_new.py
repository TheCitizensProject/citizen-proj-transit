import requests
import os
import zipfile
import datetime

directory_list = os.listdir()

if "metadata_old" in directory_list:
    print("Error: Cannot Download new data")
else:
    #keep copy of previous data
    os.rename("metadata", "metadata_old")

    #create a new dir
    os.mkdir("metadata")
    os.mkdir("metadata/ferry_data")
    os.mkdir("metadata/tram_data")

    data_files = {
        "ferry_data": "http://nycferry.connexionz.net/rtt/public/utility/gtfs.aspx",
        "tram_data": "http://rapid.nationalrtap.org/GTFSFileManagement/UserUploadFiles/7707/gtfs.zip"
    }

    #download ferry and tram static files:
    for data_dir, url in data_files.items():
        filename = f"metadata/{data_dir}/data.zip"
        response = requests.get(url)

        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {filename}")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
        
        zip_file = filename
        output_folder = f"metadata/{data_dir}/google_transit"

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(output_folder)

        print(f"Unzipped {zip_file} to {output_folder}")
    
    #download MTA Stations.csv file:
    filename = f"metadata/Stations.csv"
    url = "https://atisdata.s3.amazonaws.com/Station/Stations.csv"
    response = requests.get(url)

    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
    
    #put a timestamp tag in the new file to keep track
    today = datetime.datetime.now()
    tag = f"Data version {today}"

    with open("metadata/data-tag.txt", 'w') as file:
        file.write(tag)


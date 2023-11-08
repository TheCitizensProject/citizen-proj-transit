import os
import shutil

directory_list = os.listdir()

if "metadata" in directory_list and "metadata_old" in directory_list:
    directory_to_remove = "metadata"
    try:
        shutil.rmtree(directory_to_remove)
        print(f"Directory {directory_to_remove} removed successfully.")
    except Exception as e:
        print(f"An error occurred while removing the directory: {str(e)}")

    os.rename("metadata_old", "metadata")
    print("Old data restored")
else:
    print("Error: Delete Operation cannot be performed on Existing data")

import datetime
import os
import json
import subprocess

root_folder = "~/Downloads/Google Photos/"

def convert_to_exifdate(unix_timestamp):
    dt = datetime.datetime.fromtimestamp(int(unix_timestamp))
    return dt.strftime('%Y:%m:%d %H:%M:%S')

def find_and_modify_timestamps(root_folder):
    for root, _, files in os.walk(root_folder):
        for filename in files:
            if filename.endswith(".json"):
                json_path = os.path.join(root, filename)
                media_path = os.path.splitext(json_path)[0]  # Remove .json extension
                media_extensions = [".jpg", ".jpeg", ".heic", ".mov"]

                #if any(os.path.isfile(media_path + ext) for ext in media_extensions):
                with open(json_path, 'r', encoding='utf-8') as json_file:
                    json_data = json.load(json_file)
                    if "creationTime" in json_data:
                        timestamp = convert_to_exifdate(json_data["photoTakenTime"]["timestamp"])
                        utimestamp = convert_to_exifdate(json_data["creationTime"]["timestamp"])
                        try:
                            subprocess.run(["exiftool", "-overwrite_original", f"-CreateDate={timestamp}", f"-ModifyDate={utimestamp}", media_path])
                        except Exception:
                            print("ERROR:" + media_path)
if __name__ == '__main__':
    find_and_modify_timestamps(root_folder)
    print("Timestamps updated for relevant media files.")

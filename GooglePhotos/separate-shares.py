import os
import json
import sys

root_folder = "/Users/makos/Downloads/Zoli/Google/Google Fotók"

# Folder contents
# - *.JPG
# - *.JPG.json
meta_ext = ".json"

def find_files_with_metadata(root_folder):
    matching_files = []

    for root, _, files in os.walk(root_folder):
        for filename in files:
            if filename.endswith(meta_ext):
                json_path = os.path.join(root, filename)
                media_path = os.path.splitext(json_path)[0]  # Remove .json extension
                #media_extensions = [".heic", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".avi", ".mkv"]

                #if any(os.path.isfile(media_path + ext) for ext in media_extensions):
                with open(json_path, 'r', encoding='utf-8') as json_file:
                    json_data = json.load(json_file)
                    if "googlePhotosOrigin" in json_data and \
                        "fromSharedAlbum" in json_data["googlePhotosOrigin"] and \
                        not json_data["googlePhotosOrigin"]["fromSharedAlbum"]:
                        matching_files.append(media_path)

    return matching_files

if __name__ == '__main__':
    move_folder = root_folder + "(Shares)"
    matching_files = find_files_with_metadata(root_folder)

    if matching_files:
        print("Files with 'googlePhotosOrigin' metadata matching the criteria:")
        for file_path in matching_files:
            print("Moving -" + file_path)
            
            try:
                move_path =  file_path.replace(root_folder, move_folder)
                print(move_path)

                parents = os.path.split(move_path)[0]
                os.makedirs(parents, exist_ok=True)

                os.rename(file_path + meta_ext, move_path + meta_ext)
                os.rename(file_path, move_path)

            except Exception:
                #tb = sys.exception().__traceback__
                print("Error: " + file_path + "\n")
    else:
        print("No matching files found.")

#! /usr/bin/python

import os
import re
import glob
import csv
import subprocess


from mutagen.easyid3 import EasyID3
from fuzzywuzzy import process

takeout_csv = '/Users/akos.murati/Downloads/Music/music-uploads-metadata2.csv'
tag_lookup = {}

path = '/Users/akos.murati/Downloads/Music/_mess' #os.getcwd()
fpath = u"%s/*.mp3" % path
files = glob.glob(fpath)

def title_hash(orig):
    return re.sub(r'[\W\d]','',orig.lower())

# Build tag Lookup hash
with open(takeout_csv) as csvfile:
    tagreader = csv.DictReader(csvfile)
    for row in tagreader:
        tag_lookup[title_hash(row['Title'].lower())]=row

# Fix MP3 tags
for fname in files:
    print('\n\n>>> PROCESSING: ',fname)
    # Reeading IDv3 Tags
    file_tags = EasyID3(fname)
    print('\tMP3 tags:', file_tags)

    # Getting lookup title
    file_name=fname.split('/')[-1]
    name=re.sub('.mp3$','',file_name)
    lookup_title = title_hash(name)
    print('\tLookup tags:\n\t - ', lookup_title)
    
    # Lookup by file
    tag=tag_lookup.get(lookup_title)

    # If Unsuccessful try lookup by tag
    if (tag == None and file_tags.get('title') != None):
        lookup_title = title_hash(file_tags.get('title')[0])
        print('\t - ', lookup_title, "(by TAG title)")
        tag=tag_lookup.get(lookup_title)

    # Fuzzy match as last resort
    if (tag == None):
        closest = process.extractOne(lookup_title,tag_lookup.keys())
        print('\t - ', closest[0], "(by ~", closest[1], '% fuzzy proximity)')
        tag=tag_lookup.get(closest[0])

    # Reconciling
    if (tag):
        change = False
        print("\tMATCHED:", fname, ' == ', tag)

        change =  file_tags.get('title') == None or file_tags.get('album') == None or file_tags.get('artist') == None \
            or ( file_tags.get('title') and file_tags.get('title')[0] != tag['Title']) \
            or ( file_tags.get('album') and file_tags.get('album')[0] != tag['Album']) \
            or ( file_tags.get('artist') and file_tags.get('artist')[0] != tag['Artists'])
        
        if change:
            file_tags["title"] = tag['Title']
            file_tags["album"] = tag['Album']
            file_tags["artist"] = tag['Artists']
            print(file_tags)
            file_tags.save()
            print("<<< OK: Tags saved")
        else:
            print("<<< OK: Nothing to change")

    else:
        print("<<< ERROR: NOT FOUND", fname)
        continue
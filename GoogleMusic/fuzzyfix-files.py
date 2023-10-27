#! /usr/bin/python

import os
import re
import glob
import csv
import subprocess

from mutagen.easyid3 import EasyID3
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

converter = re.compile(r'[-_\(\)]',re.U)

takeout_csv = '~/Downloads/Music/music-uploads-metadata2.csv'
path = '~/Downloads/Music/_mess' #os.getcwd()
tag_lookup = {}
skip_first = 0

fpath = u"%s/*.mp3" % path


def convert_simple(orig):
    new = converter.sub('',orig.lower())
    return new.strip()


def lookup_fuzzy(pattern):
    closest = process.extractOne(pattern.lower(),tag_lookup.keys(),scorer=fuzz.UQRatio)
    print('\t - ', closest[0], "(by ~", closest[1], '% fuzzy proximity)')
    if (closest[1]<60):
        print('\t WARNING: too fuzzy..')
        return None
    return tag_lookup.get(closest[0])

# Build tag Lookup hash
with open(takeout_csv) as csvfile:
    tagreader = csv.DictReader(csvfile)
    for row in tagreader:
        title_only = row['Title'].lower()
        full = '{0} - {1}'.format(row['Artists'], row['Title']).lower()

        tag_lookup[title_only]=row
        tag_lookup[convert_simple(title_only)]=row
        #tag_lookup[full]=row
        #tag_lookup[convert_simple(full)]=row

# Fix MP3 tags
c=0
files = glob.glob(fpath)
total = 0 #files.len()
for fname in files:
    c=c+1
    print('\n\n>>> FILE {0}/{1}: {2}'.format(c,total,fname))

    if (c<skip_first):
        print('<<< SKIP.')

    # Reeading IDv3 Tags
    file_tags = EasyID3(fname)
    print('\tCurrent MP3 tags:', file_tags)

    # Getting lookup names
    file_name=fname.split('/')[-1]
    name=re.sub('.mp3$','',file_name)
    
    # Lookup by file name
    print('\tLookup tags:')
    print('\t - ', name)
    tag=tag_lookup.get(name.lower())

    # Lookup by file name simplified
    if (tag == None):
        lookup_title = convert_simple(name)
        print('\t - ', lookup_title)
        tag=tag_lookup.get(lookup_title)

    # # If Unsuccessful try lookup by tag
    # if (tag == None and file_tags.get('title') != None):
    #     lookup_title = convert_simple(file_tags.get('title')[0])
    #     print('\t - ', lookup_title, "(by TAG title)")
    #     tag=tag_lookup.get(lookup_title)

    # Fuzzy match as last resort
    #if (tag == None):
    #    tag=lookup_fuzzy(name)

    if (tag == None):
        tag=lookup_fuzzy(convert_simple(name))

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
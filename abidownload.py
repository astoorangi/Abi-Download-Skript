#!/bin/env python

import argparse
from pdfminer.high_level import extract_text
from webdav3.client import Client
import os
import re
import json

parser = argparse.ArgumentParser()
parser.add_argument("input_directory")
parser.add_argument("output_directory")
args = parser.parse_args()

input_directory = args.input_directory
output_directory = args.output_directory

# find all pdfs

credentials_pdfs = [
    f
    for f in os.listdir(input_directory)
    if re.match(r"\d{4}-\d{2}-\d{2}_\d+-(.+)+\.pdf", f)
]

documentation = {}

for pdf in credentials_pdfs:
    # parse pdf

    pdfcontent = extract_text(os.path.join(input_directory, pdf)).splitlines()
    subject = pdfcontent[0][:-1]
    year = pdfcontent[2][:4]
    share_id = pdfcontent[2].split("/")[-1][:-1]
    share_password = pdfcontent[4][:-1]

    # download from ownCloud

    download_location = os.path.join(output_directory, subject, year)
    try:
        # create download directory
        os.makedirs(download_location)
    except FileExistsError:
        pass

    options = {
        "webdav_hostname": "https://membox.nrw.de/remote.php/dav/public-files/" + share_id,
        "webdav_login": "public",
        "webdav_password": share_password,
    }

    client = Client(options)
    filenames = client.list()
    for file in filenames[1:]:
        client.download_sync(remote_path=file, local_path=os.path.join(download_location, file))
        try:
            documentation[subject][year].append(file)
        except KeyError: # year does not exist for subject in documentation
            try:
                documentation[subject][year] = []
                documentation[subject][year].append(file)
            except KeyError: # subject does not exist in documentation
                documentation[subject] = {}
                documentation[subject][year] = []
                documentation[subject][year].append(file)
        
with open(os.path.join(output_directory, "documentation.json"), 'w') as file: 
     file.write(json.dumps(documentation))

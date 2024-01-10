#!/bin/env python

import argparse
from pdfminer.high_level import extract_text
from webdav3.client import Client
from webdav3.exceptions import WebDavException
import os
import re
import json

def find_all_credential_pdfs(path):
    credential_pdfs = [
        f
        for f in os.listdir(path)
        if re.match(r"\d{4}-\d{2}-\d{2}_\d+-(.+)+\.pdf", f)
    ]
    return credential_pdfs

def parse_credential_pdf(path_to_file):
    pdfcontent = extract_text(path_to_file).splitlines()
    subject = re.search(r'([^\/]+)', pdfcontent[0]).group(1)[:-1]
    year = pdfcontent[2][:4]
    share_id = pdfcontent[2].split("/")[-1][:-1]
    share_password = pdfcontent[4][:-1]
    return subject, year, share_id, share_password

def download_all_files_from_share(share_id, share_password, subject, year, download_directory):
    download_location = os.path.join(download_directory, subject, year)
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
    try:
        filenames = client.list()
    except WebDavException as exception:
        print(f"{subject} {year} failed ls! Share-ID: {share_id}")
        return
    for file in filenames[1:]:
        print(f"Downloading {subject} {year}: {file}")
        try:
            client.download_sync(remote_path=file, local_path=os.path.join(download_location, file))
        except WebDavException as exception:
            print(f"{file}: failed!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory")
    parser.add_argument("output_directory")
    parser.add_argument("-nd", "--no-download", action='store_true', help="parsing pdfs without downloading files")
    args = parser.parse_args()

    input_directory = args.input_directory
    output_directory = args.output_directory

    credentials = []

    credential_pdfs = find_all_credential_pdfs(input_directory)
    for pdf in credential_pdfs:
        subject, year, share_id, share_password = parse_credential_pdf(os.path.join(input_directory, pdf))
        credentials.append({"subject": subject, "year": year, "share_id": share_id, "share_password": share_password})
    
    for credential in credentials:
        download_all_files_from_share(credential["share_id"], credential["share_password"], credential["subject"], credential["year"], output_directory)

if __name__ == "__main__":
    main()

"""
    # download from ownCloud
    if args.no_download:
        continue


        try:
            documentation[subject][year].append(file)
        except KeyError: # subject or year does not exist in documentation
            documentation[subject] = {} if subject not in documentation else documentation[subject]
            documentation[subject][year] = [] if year not in documentation[subject] else documentation[subject][year]
            documentation[subject][year].append(file)

with open(os.path.join(output_directory, "documentation.json"), 'w') as file: 
     file.write(json.dumps(documentation))
"""
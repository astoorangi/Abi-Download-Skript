#!/bin/env python

import argparse
from pdfminer.high_level import extract_text
from webdav3.client import Client
from webdav3.exceptions import WebDavException
import os
import re


def find_all_credential_pdfs(path):
    credential_pdfs = [
        f
        for f in os.listdir(path)
        if re.match(r"\d{4}-\d{2}-\d{2}_\d+-(.+)+\.pdf", f)
        or f == "allefcher2007-2021.pdf"
    ]
    return credential_pdfs


def sanitize_subject(name):
    return re.search(r"([^\/]+)", name).group(1)[:-1]


def parse_credential_pdf(path_to_file):
    pdfcontent = extract_text(path_to_file).splitlines()
    if pdfcontent[0] == "Alle Fächer 2007-2021 (soweit geprüft) ":
        return parse_all_in_one_pdf(pdfcontent)
    details = {}
    details["subject"] = sanitize_subject(pdfcontent[0])
    details["year"] = pdfcontent[2][:4]
    details["share_id"] = pdfcontent[2].split("/")[-1][:-1]
    details["share_password"] = pdfcontent[4][:-1]
    return [details]


def collect_all_in_one_pdf_credentials(content):
    subject = None
    working_list = []
    for line in content:
        print(line)
        if re.match(r"\d{4} ", line):
            working_list = [line] + working_list
        else:
            if subject is None:
                subject = sanitize_subject(line)
                continue
            share_password = line
            for entry in working_list:
                year = entry[:4]
                share_id = entry[len('XXXX  https://membox.nrw.de/index.php/s/'):]
                yield {
                    'subject': subject,
                    'year': year,
                    'share_id': share_id,
                    'share_password': share_password,
                }
            working_list = []
            subject = None


def parse_all_in_one_pdf(pdfcontent):
    pdfcontent = [
        line[:-1] for line in pdfcontent
    ]  # Remove last character (" ") in each line
    pdfcontent = list(filter(None, pdfcontent))[2:]  # Remove all empty strings in list
    return [credential for credential in collect_all_in_one_pdf_credentials(pdfcontent)]


def download_all_files_from_share(
    share_id, share_password, subject, year, download_directory
):
    download_location = os.path.join(download_directory, subject, year)

    options = {
        "webdav_hostname": "https://membox.nrw.de/remote.php/dav/public-files/"
        + share_id,
        "webdav_login": "public",
        "webdav_password": share_password,
    }
    client = Client(options)

    # list all available files in share
    sucessful, i = False, 0
    while not sucessful:
        try:
            filenames = client.list()
            sucessful = True
        except WebDavException as exception:
            i += 1
            if i == 5:
                print(
                    f"""Failed fetching shared files!
                Share-ID: {share_id}
                Share Password: {share_password}
                Subject: {subject}
                Year: {year}"""
                )
                return
            print(f"Retry... ({subject})")
            pass

    # create download directory
    try:
        os.makedirs(download_location)
    except FileExistsError:
        pass

    # download all files in share
    for file in filenames[1:]:
        print(f"Downloading {subject} {year}: {file}")
        sucessful, i = False, 0
        while not sucessful:
            try:
                client.download_sync(
                    remote_path=file, local_path=os.path.join(download_location, file)
                )
                sucessful = True
            except WebDavException as exception:
                i += 1
                if i == 5:
                    print(f"{file}: failed!")
                    break
                print(f"Retry... ({file})")
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory")
    parser.add_argument("output_directory")
    args = parser.parse_args()

    input_directory = args.input_directory
    output_directory = args.output_directory

    credentials = []

    credential_pdfs = find_all_credential_pdfs(input_directory)
    for pdf in credential_pdfs:
        credentials += parse_credential_pdf(os.path.join(input_directory, pdf))

    for credential in credentials:
        download_all_files_from_share(
            credential["share_id"],
            credential["share_password"],
            credential["subject"],
            credential["year"],
            output_directory,
        )


if __name__ == "__main__":
    main()

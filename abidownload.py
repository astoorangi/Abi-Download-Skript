#!/bin/env python

from pdfminer.high_level import extract_text
from webdav3.client import Client

# PDF parsen

pdfcontent = extract_text(filename).splitlines()
fach_name = pdfcontent[0][:-1]
jahr = pdfcontent[2][:4]
share_id = pdfcontent[2].split("/")[-1][:-1]
share_password = pdfcontent[4][:-1]


# Download aus ownCloud

link_to_cloud = "https://membox.nrw.de/remote.php/dav/public-files/"

options = {
    "webdav_hostname": link_to_cloud + share_id,
    "webdav_login": "public",
    "webdav_password": share_password,
}

client = Client(options)
filenames = client.list()

for file in filenames[1:]:
    # Wirft Fehler, da Ordner nicht existieren:
    # client.download_sync(remote_path=file, local_path=f"{file[2:4]}/{file[0:2]}/{file}")
    client.download_sync(remote_path=file, local_path=f"{file}")

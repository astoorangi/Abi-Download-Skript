#!/bin/env python

from webdav3.client import Client

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

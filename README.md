# flask-fileserver-demo
Flask web server for demonstrating a very basic cloud file storage

To start, simply run `python3 app.py`.

This script creates a server which allows managing files, sort of like a cloud storage service.
It's a very basic server with almost zero CSS and (obviously) no security features like a login system or encryption.
It allows uploading, listing, downloading, renaming and deleting files.

*Note #1*: The `Kind` column shows different results based on your OS. On macOS it shows the same information as displayed in the `Kind` column in Finder. On Linux it displays the `mime-type` from the `file` command. On Windows it just shows the file extension.  
*Note #2*: The `Date added` column shows different results based on your OS. On macOS and Linux it shows time based on `st_birthtime` from `os.path(file)`. On Windows it shows `st_mtime` from the same function, as Windows does not support `st_birthtime`.

⚠️ This project is just for demo purposes. Don't use it on a production server.

Used tools and sources:  
HTML Editor site: https://www.quackit.com/html/online-html-editor/full/   
Flask doc: https://flask.palletsprojects.com/en/2.1.x/

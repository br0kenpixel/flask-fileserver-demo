from flask import Flask
from flask import send_from_directory
from flask import request
from flask import redirect
from flask import render_template
from flask import send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from pathlib import Path
from sys import platform
from os import scandir, stat

if platform == "darwin":
	from AppKit import NSWorkspace
	from LaunchServices import UTTypeCopyDescription
	from Cocoa import NSURL, NSURLLocalizedTypeDescriptionKey

	def getFileKind(file):
		file = "storage/" + file
		uti = NSWorkspace.sharedWorkspace().typeOfFile_error_(file, None)[0]
		desc = UTTypeCopyDescription(uti)

		url = NSURL.fileURLWithPath_(file)
		urlType = url.getResourceValue_forKey_error_(None, NSURLLocalizedTypeDescriptionKey, None)[1]
		return urlType

elif "win" not in platform:
	from subprocess import run

	def getFileKind(file):
		file = "storage/" + file
		raw = run(f"file --mime-type {file}", shell=True, capture_output=True).stdout
		return raw[raw.index(b":") + 2:].decode().strip()
else:
	def getFileKind(file):
		if "." not in file:
			return "Unknown"
		return file[file.rindex(".") + 1:].upper()

def getFileCreationDate(file):
	file = "storage/" + file
	if "win" not in platform:
		creationDate = stat(file).st_birthtime
	else:
		creationDate = stat(file).st_mtime
	creationDate = datetime.fromtimestamp(creationDate)
	return creationDate.strftime("%d.%m.%Y %H:%M:%S")

app = Flask(__name__, template_folder="web")

def serveDocFile(file):
	return render_template(file)

def getFileList():
	for file in Path("storage").glob("*"):
		name = file.name
		kind = getFileKind(name)
		date_added = getFileCreationDate(name)
		size = fileSizeUnits(file.stat().st_size)
		yield (name, kind, date_added, size)

def fileExists(name):
	for file in getFileList():
		if file[0] == name:
			return True
	return False

def getFileCount():
	count = 0
	for _ in getFileList():
		count += 1
	return count

def fileSizeUnits(size):
	if size >= 1e9:
		return f"{round(size / 1e9, 2)}GB"
	elif size >= 1_000_000:
		return f"{round(size / 1_000_000, 2)}MB"
	elif size >= 1000:
		return f"{round(size / 1000, 2)}kB"
	else:
		return f"{size}B"

def getUsedStorage():
	return fileSizeUnits(sum(file.stat().st_size for file in scandir("storage")))

def renderFilesPage():
	date = datetime.now()
	weekday = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")[date.weekday()]
	date = f"{date.day}.{date.month}.{date.year} ({weekday})"
	return render_template("root.html", date=date, file_count=getFileCount(), size=getUsedStorage(), files=getFileList())

def handleRenameRequest(src, dest):
	if secure_filename(dest) != dest:
		return "Access Denied - Insecure path", 401
	if fileExists(dest):
		return "Bad Request - File already exists", 400
	Path(f"storage/{src}").rename(f"storage/{dest}")
	return redirect("/")

@app.route("/get", methods=["GET"])
def download():
	args = request.args
	if args.get("file", None) == None:
		return "Bad Request - No file specified", 400
	file = args.get("file")
	if secure_filename(file) != file:
		return "Access Denied - Insecure path", 401
	return send_from_directory("storage", file, as_attachment=True)

@app.route("/del")
def delete():
	args = request.args
	if args.get("file", None) == None:
		return "Bad Request - No file specified", 400
	file = args.get("file")
	if not fileExists(file):
		return "Bad Request - File does not exist", 400
	if secure_filename(file) != file:
		return "Access Denied - Insecure path", 401
	Path(f"storage/{file}").unlink()
	return redirect("/")

@app.route("/rename", methods=["GET"])
def rename():
	args = request.args
	src = args.get("file", None)
	dest = args.get("dest", None)

	if src == None:
		return "Bad Request - No source file", 400
	if secure_filename(src) != src:
		return "Access Denied - Insecure path", 401
	if dest != None:
		return handleRenameRequest(src, dest)
	return render_template("rename.html", src=src)

@app.route("/upload", methods=["GET", "POST"])
def upload():
	if request.method == "GET":
		return serveDocFile("upload.html")
	else:
		if 'file' not in request.files:
			return "Bad Request - POST missing file", 400
		file = request.files['file']
		if file.filename == "":
			return "Bad Request - No file selected", 400

		filename = secure_filename(file.filename)
		if fileExists(filename):
			return "Bad Request - File already exists", 400
		file.save(f"storage/{filename}")

		return redirect("/")

@app.route("/", methods=['GET'])
def root():
	return renderFilesPage()

app.run(port=8080)
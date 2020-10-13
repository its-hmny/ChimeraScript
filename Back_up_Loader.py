"""
Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script 
works recursively so (as the example show) you only need to put the directory you want to upload and it will automate the 
process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal)

Note: it requires pysftp as third party library, you can install it with "pip3 install pysftp"

Created by Enea Guidi on 08/11/2019. Please check the README.md for more informations 
"""

import pysftp, getpass, platform, os, sys
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import SSHException
from utility import Log, Compressor

# Fixed fields for every OS (platform indipendent)
destPath = "/public/hmny/" # The destinaion path on the server
destFolder = destPath + "Backup/"
hostname = "pinkerton.cs.unibo.it"
usrnm = "enea.guidi"
dirBlacklist = ["node_modules"]

log = Log()

# Platform specific fields
if (platform.system() == "Windows"):
	homePath = "C:/Users/eneag/"
	dirToUpload = ["Pictures", "Desktop/Progetti", "Desktop/Università", "Documents"]
elif (platform.system() == "Linux"):
	homePath = "/home/hmny/"
	dirToUpload = ["Pictures", "Projects", "University", "Documents"]
else:
	log.error("This OS is not supported yet")
	os._exit(os.EX_OSERR)

def recursivePut(sftpConnection, toUpload, destination):
	try:
		for entry in os.listdir(toUpload):
			local = os.path.join(toUpload, entry)
			remote = destination + "/" + entry
			
			if os.path.isdir(local) and dirBlacklist.count(entry) == 0:
				sftpConnection.makedirs(remote)
				recursivePut(sftpConnection, local, remote)
				continue
			elif os.path.islink(local):
				continue
			elif os.path.isfile(local):
				sftpConnection.put(local, remote)
	except PermissionError:
		log.error(toUpload + " couldn't be opened")

def uncompressedUpload(sftp):
	# Creates the destination if it doesn't exist
	sftp.makedirs(destFolder)
	# Private access to only owner
	sftp.chmod(destPath, mode=700)	
	sftp.chdir(destFolder)

	for up_dir in dirToUpload:
		cwd = homePath + up_dir
		remote_cwd = destFolder + up_dir.split("/")[-1]
		sftp.makedirs(remote_cwd)
		recursivePut(sftp, cwd, remote_cwd)
		log.success(cwd + " has been uploaded")

def compressedUpload(sftp):
	# Put all the desired directory in a compressed file
	dump = Compressor(homePath + "Backup.zip")
	for up_dir in dirToUpload:
		dump.compressDir(homePath + up_dir, blacklist=dirBlacklist)
		log.success("{} compressed".format(up_dir))
	
	if errors := dump.runChecks():
		log.error("Test on the compressed archive returned errors: {}".format(errors))
	
	del dump

	# Creates the destination path with the correct attributes
	sftp.makedirs(destPath)
	sftp.chmod(destPath, mode=700)	
	sftp.chdir(destPath)

	sftp.put(homePath + "Backup.zip", destPath)
	os.remove(homePath + "Backup.zip")

def Back_up_Loader():
	try:
		mode = sys.argv[1]
		pswd = getpass.getpass(prompt="Please insert password: ")
		with pysftp.Connection(host=hostname, username=usrnm, password=pswd) as sftp:
			log.warning("Connection established")
			
			if mode == "--compressed" or mode == "-c":
				compressedUpload(sftp)
			elif mode == "--uncompressed" or mode == "-u":
				uncompressedUpload(sftp)
			else:
				log.error("Unrecognized arg: {}".format(mode))

			sftp.close()

	except AuthenticationException:
		log.error("Authentication failed, username or password invalid")

	except SSHException:
		log.error("Could not connect to the host")

	except IndexError:
		log.warning("""
			You should provide an additional argument: python3 Back_UP_Loader.py [mode]
			where mode could be:
			  -c or --compressed     to upload a compressed dump of all the directories
			  -u or --uncompressed   to upload the directories themselves without any type of compression
			""")


Back_up_Loader()
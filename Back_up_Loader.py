"""
Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script 
works recursively so (as the example show) you only need to put the directory you want to upload and it will automate the 
process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal)

Note: it requires pysftp as third party library, you can install it with "pip3 install pysftp"

Created by Enea Guidi on 08/11/2019. Please check the README.md for more informations 
"""

import pysftp, getpass, platform, os
from paramiko.ssh_exception import AuthenticationException
from utility import Log

# Fixed fields for every OS (platform indipendent)
destPath = "/public/hmny/" # The destinaion path on the server
destFolder = destPath + "Backup/"
hostname = "pinkerton.cs.unibo.it"
usrnm = "enea.guidi"

log = Log()

# Platform specific fields
if (platform.system() == "Windows"):
	homePath = "C:/Users/eneag/"
	dirToUpload = ["Pictures"]#, "Desktop/Progetti", "Desktop/Università", "Documenti"]
elif (platform.system() == "Linux"):
	homePath = "/home/hmny/"
	dirToUpload = ["Pictures", "Projects", "University", "Documents"]
else:
	log.errorMsg("This OS is not supported yet")
	os._exit(os.EX_OSERR)


def recursivePut(sftpConnection, toUpload, destination):
	for entry in os.listdir(toUpload):
		local = os.path.join(toUpload, entry)
		remote = destination + "/" + entry
		
		if os.path.isdir(local):
			sftpConnection.makedirs(remote)
			recursivePut(sftpConnection, local, remote)
			continue
		elif os.path.islink(local):
			continue
		
		sftpConnection.put(local, remote)


def Back_up_Loader():
	pswd = getpass.getpass(prompt="Please insert password: ")
	try:
		with pysftp.Connection(host=hostname, username=usrnm, password=pswd) as sftp:
			log.warningMsg("Connection established")
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
				log.successMsg(cwd + " has been uploaded")

			sftp.close()

	except AuthenticationException:
		log.errorMsg("Authentication failed, username or password invalid")


Back_up_Loader()
"""
Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script 
works recursively so (as the example show) you only need to put the directory you want to upload and it will automate the 
process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal)

Note: it requires pysftp as third party library, you can install it with "pip3 install pysftp"

Created by Enea Guidi on 08/11/2019. Please check the README.md for more informations 
"""

import pysftp, getpass, platform, os, paramiko
from pathlib import Path

# Fixed fields for every OS (platform indipendent)
destPath = "/public/hmny/" # The destinaion path on the server
destFolder = destPath + "Backup/"
homePath = Path.home()
hostname = "pinkerton.cs.unibo.it"
usrnm = "enea.guidi"

success = "\033[92m"
error = "\033[91m"
clear = "\033[0m"

# Platform specific fields
if (platform.system() == "Windows"):
	dirToUpload = ["Immagini", "Desktop/Progetti", "Desktop/Università", "Documenti"]
elif (platform.system() == "Linux"):
	dirToUpload = ["Pictures", "Projects", "University", "Documents"]
else:
	print(fail + "This OS is not supported yet" + clear)
	os._exit(os.EX_OSERR)


def Back_up_Loader():
	pswd = getpass.getpass(prompt="Please insert password: ")
	try:
		with pysftp.Connection(host=hostname, username=usrnm, password=pswd) as sftp:
			print("Connection established")
			# Creates the destination if it doesn't exist
			sftp.makedirs(destFolder)
			# Private access to only owner
			sftp.chmod(destPath, mode=700)	
			sftp.chdir(destFolder)

			for up_dir in dirToUpload:
				cwd = homePath / up_dir
				sftp.makedirs(destFolder + up_dir.split("/")[-1])
				#sftp.put_r(cwd, destFolder + up_dir)
				print(success + str(cwd) + " has been uploaded" + clear)

			sftp.close()

	except paramiko.ssh_exception.AuthenticationException:
		print(error + "Authentication failed, username or password invalid" + clear)


Back_up_Loader()
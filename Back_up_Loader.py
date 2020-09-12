"""
Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script 
works recursively so (as the example show) you only need to put the directory you want to upload and it will automate the 
process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal)
Created by Enea Guidi on 08/11/2019. Please check the README.md for more informations 
"""

import pysftp, getpass

homePath = "/home/hmny/" #Your initial path 
destPath = "/public/hmny/" #The destinaion path on the server
destFolder = destPath + "Backup/"
dirToUpload = ["Pictures", "Projects", "University", "Documents"]
hostname = "pinkerton.cs.unibo.it"
usrnm = "enea.guidi"


def Back_up_Loader():
	pswd = getpass.getpass(prompt="Please insert password: ")
	
	with pysftp.Connection(host=hostname, username=usrnm, password=pswd) as sftp:
		print("Connection established")
		sftp.makedirs(destFolder) #Creates the destination if it doesn't exist
		sftp.chmod(destPath, mode=700)	#Private access to only owner	
		sftp.chdir(destFolder)

		for up_dir in dirToUpload:
			cwd = homePath + up_dir
			sftp.makedirs(destFolder + up_dir)
			sftp.put_r(cwd, destFolder + up_dir)
			print(cwd + " has been uploaded")

		sftp.close()


Back_up_Loader()
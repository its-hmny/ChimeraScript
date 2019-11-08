#Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script 
#works recursively so (as the example show) ypu only need to put the directory you want to upload and it will automate the 
#process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal)
# Created by Enea Guidi on 08/11/2019. Please check the README.md for more informations 

import pysftp

homePath = "/home/hmny/" #Your initial path
dirToUpload = ["Pictures", "Desktop/Projects", "Desktop/University", "Documents"]
hostname = "-> YOUR SFMTP SERVER"
myUsername = "-> YOUR USERNAME"


def Back_up_Loader():
	myPassword = input("Please insert password: ")
	
	with pysftp.Connection(host=hostname, username=myUsername, password=myPassword) as sftp:
		print("Connection established")

		for up_dir in dirToUpload:
			cwd = homePath + up_dir
			sftp.put_r(cwd, "/public/hmny/Backup/")
			print(cwd + " has been uploaded")

		sftp.close()


Back_up_Loader()
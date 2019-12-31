#Back_up_Loader is a simple Python scipt used to automate my regular backup upload to the university sftp server, this script 
#works recursively so (as the example show) ypu only need to put the directory you want to upload and it will automate the 
#process for you. PLEASE NOTE THAT THIS WON'T WORK ON WINDOWS (due to the use of \ instead of / in Windows terminal)
# Created by Enea Guidi on 08/11/2019. Please check the README.md for more informations 

import pysftp

homePath = "/home/hmny/" #Your initial path
destPath = "/public/hmny/Backup/" #The destinaion path on the server
dirToUpload = ["Pictures", "Templates", "University", "Documents"]
hostname = "pinkerton.cs.unibo.it"
myUsername = "enea.guidi"


def Back_up_Loader():
	myPassword = input("Please insert password: ")
	
	with pysftp.Connection(host=hostname, username=myUsername, password=myPassword) as sftp:
		print("Connection established")
		sftp.makedirs(destPath) #Creates the destination if it doesn't exist
		sftp.chdir(destPath)

		for up_dir in dirToUpload:
			cwd = homePath + up_dir
			sftp.makedirs(destPath + up_dir)
			sftp.put_r(cwd, destPath + up_dir)
			print(cwd + " has been uploaded")

		sftp.close()


Back_up_Loader()
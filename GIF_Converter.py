"""
GIF_Converter is a simple script to convert a .mp4 or .mkv file to a .gif file, 
more extension type to convert coming soon...

Note: In order to work it relies on imageio as third party library,
you can install with "pip3 install imageio" from command line

Created by Enea Guidi on 31/08/2019, please check the Readme.md for more information.
"""

import imageio, os, sys
from chimera_utils import Log

#Takes the two path and then copies every frame of the video to the correspondant .gif file
def video_to_Gif(input, output):
	
	reader = imageio.get_reader(input)
	fps = reader.get_meta_data()['fps']
	writer = imageio.get_writer(output, fps = fps)

	for frames in reader:
		writer.append_data(frames)

	writer.close()
	reader.close()		

def GIF_Converter():
	log = Log()
	try:
		inputPath= os.path.abspath(sys.argv[1])
		inputExtension = os.path.splitext(inputPath)[1]
		log.success('Converting....')

		if(inputExtension == '.mp4') or (inputExtension == '.mkv'):
			outputPath = os.path.splitext(inputPath)[0] + '.gif'
			video_to_Gif(inputPath, outputPath)
			log.success('Done!')
		else: 
			log.error("Unsupported file type")
	
	except IndexError:
		log.warning("Need the path to file")

GIF_Converter()
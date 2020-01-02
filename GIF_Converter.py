"""
GIF_Converter is a simple script to convert a .mp4 file to a .gif file, more extension tipe to convert coming soon...
Created by Enea Guidi on 31/08/2019, please check the Readme.md for more information.
"""
import imageio, os, sys

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
	inputPath= os.path.abspath(sys.argv[1])
	inputExtension = os.path.splitext(inputPath)[1]
	print('Converting....')

	if(inputExtension == '.mp4') or (inputExtension == '.mkv'):
		outputPath = os.path.splitext(inputPath)[0] + '.gif'
		video_to_Gif(inputPath, outputPath)
		print('Done!')
	else: 
		print("Unsupported file type")


GIF_Converter()
from moviepy.editor import VideoFileClip, clips_array, vfx,concatenate_videoclips
from config import *
import time
		
def trimVideo(videofile: str,start_time: int,end_time: int):
	
	clip = VideoFileClip(videofile)
	videofile = videofile.replace(video_savepath,"")
	trimpath = video_savepath + "edited_" + str(int(time.time())) + videofile
	trimmed_clip = clip.subclip(start_time,end_time)
	trimmed_clip.write_videofile(trimpath)
	return trimpath


def mergeVideos(videoclip_filenames):

	videoclips = []
	for filename in videoclip_filenames:
		videoclips.append(VideoFileClip(filename))

	final_clip = concatenate_videoclips(videoclips,method="compose")
	finalpath = "clips/finalrender_" + str(int(time.time())) + ".mp4"
	final_clip.write_videofile(finalpath)
	return finalpath


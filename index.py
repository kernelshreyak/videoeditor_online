from flask import Flask
from flask import request
from flask import render_template
from flask import send_file

from video_utils import trimVideo, mergeVideos
from config import config
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("video_editor.html")



@app.route('/clips/<filename>')
def render_clip(filename):
	return send_file(config.video_savepath + filename)

# Uploads a video file to server and returns filename
@app.route('/upload_video',methods=['POST'])
def upload_video():
	# check if video savepath exists
	if  not os.path.isdir("./clips"):
		os.mkdir("./clips")
	try:
		videofile = request.files['videofile']
		filepath = config.video_savepath + videofile.filename
		videofile.save(filepath)
	except FileNotFoundError:
		return "ERROR"

	return str(filepath)




# Main video editing pipeline
@app.route('/edit_video/<actiontype>',methods=['POST'])
def edit_video(actiontype):
	if actiontype == "trim":
		try:
			edited_videopath = trimVideo(request.form['videofile'],int(request.form['trim_start']),int(request.form['trim_end']))
			return {
				"status": "success",
				"message": "video edit success",
				"edited_videopath": edited_videopath
			}
		except Exception as e:
			return {
				"status": "error",
				"message": "video edit failure: " + str(e),
			}

    
@app.route('/merged_render',methods=['POST'])
def merged_render():
	try:
		videoscount = int(request.form['videoscount'])
		if videoscount > 0:
			videoclip_filenames = []
			for i in range(videoscount):
				videoclip_filenames.append(request.form['video' + str(i)])

			finalrender_videopath = mergeVideos(videoclip_filenames)
			return {
					"status": "success",
					"message": "merged render success",
					"finalrender_videopath": finalrender_videopath
				}
		else:
			return {
					"status": "error",
					"message": "merged render error. Invalid videos count"
				}
		
	except Exception as e:
		return {
			"status": "error",
			"message": "video merge failure: " + str(e),
		}


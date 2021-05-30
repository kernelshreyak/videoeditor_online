from flask import Flask
from flask import request
from flask import render_template
from flask import send_file

from video_utils import *
from config import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("video_editor.html")



@app.route('/clips/<filename>')
def renderClip(filename):
	return send_file(video_savepath + filename)

# Uploads a video file to server and returns filename
@app.route('/upload_video',methods=['POST'])
def uploadVideo():
	try:
		videofile = request.files['videofile']
		filepath = video_savepath + videofile.filename
		videofile.save(filepath)
	except:
		return "ERROR"

	return str(filepath)

# Main video 
@app.route('/edit_video/<actiontype>',methods=['POST'])
def editVideo(actiontype):
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

    

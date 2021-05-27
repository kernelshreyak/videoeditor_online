from moviepy.editor import VideoFileClip, clips_array, vfx
clip1 = VideoFileClip("video.mp4")
clip2 = clip1.subclip(10,13)
clip2.write_videofile("aaa.mp4")


<template>
    <div class="app-container">
      <div class="container-fluid p-5 text-center app-header">
        <h1>Video Editor Online</h1>
      </div>

      <div class="container-fluid">
			<br><br>
      <CustomLoader v-if="loading" />
			<div class="row">
				<div class="col-lg-6">
					<div class="align-center row">
					<b>Video Render Preview</b><br>
					<div v-if="videoToRender && originalvideos.length > 0" style="width: 100%;max-width: 100%;">
						<video :src="'http://localhost:5000/' + videoToRender" controls></video>
					</div>
          <div v-else>
            <div class="alert alert-warning">No video loaded</div>
          </div>
				</div>
				</div>

				<div class="col-lg-6">
					<div class="col-sm-12">
						<div class="form-group">
							<label for="fileinput">Add Video Clip:</label>
							<input type="file" id="fileinput" accept="video/*"> 
							<div class="col-sm-4" style="padding-left: 0"> <br>
								<input type="text" class="form-control" placeholder="Clip Name" 
								id="clipname">
							</div>
								
						</div>
						<br>
						<div class="col-sm-4">
							<button class="btn btn-primary" v-on:click="uploadVideoFile">
								 Upload
							</button>
						</div>
					</div>
					<div class="col-sm-12" style="padding: 50px;">
						 <div class="progress" v-if="uploadprogress > 0">

						  <div id="uploadprogress" class="progress-bar progress-bar-success" role="progressbar" :aria-valuenow="uploadprogress"
						  aria-valuemin="0" aria-valuemax="100" style="width:0%">
						    
						  </div>
						</div> 
					</div>
			
					<div class="row videodiv" v-for="(video,index) in videos" :key="index">
                        <div class="video-card-head">
                            <input :disabled="true" type="text" :value="video.name" />
                            <h3><u></u> </h3>
                            <div>
                                <i v-on:click="() => {}" class="bi bi-pencil" style="font-size: 30px;color: green; cursor: pointer;"></i>

                                <i v-on:click="() => {removeVideo(index)}" class="bi bi-trash" style="font-size: 30px;color: red; cursor: pointer;margin-left: 1rem;"></i>
                            </div>

                        </div>
						

						<div class="video-controls" style="margin-top: 1rem;">
                            <button v-on:click="() => {setRenderVideo(index)}" class="btn btn-success video-ctrl-btn">Render/Preview</button>
						<button class="btn btn-primary btn-sm video-ctrl-btn" v-on:click="reloadOriginalVideo(index)">
							Reload Original Video
						 </button>
                        </div>
						<div class="align-center" style="margin-top: 50px;">
							<h4>Video Effects</h4>
							<b>Trim</b>
							<div class="form-group">
								<div class="col-sm-4">
									<label for="start">Start:</label>
									<input min="0" max="120" type="number" :id="`trim_start`+index" 
									value="0">
								</div>
								<div class="col-sm-4">
									<label for="end">End:</label>
									<input min="0" max="120" type="number" :id="`trim_end`+index" 
									value="0">
								</div>
								<div class="col-sm-3">
									<button class="btn btn-warning" v-on:click="editVideoSubmit(index,'trim')">Trim</button>
								</div>		
							</div>
						</div>
					</div>
					<br> <br>
					<div v-if="videos.length > 0" class="col-sm-3">
						<button class="btn btn-success" v-on:click="finalrender">Merge Clips</button>
					</div>	
				</div>
			</div>
		</div>
    </div>
</template>

<style>

.loader {
    border: 16px solid #f3f3f3;
    border-radius: 50%;
    border-top: 16px solid #3498db;
    width: 120px;
    height: 120px;
    -webkit-animation: spin 2s linear infinite; /* Safari */
    animation: spin 2s linear infinite;
  }
  
  /* Safari */
  @-webkit-keyframes spin {
    0% { -webkit-transform: rotate(0deg); }
    100% { -webkit-transform: rotate(360deg); }
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  video {
    width: 100%;
    height: auto;
    max-height: 500px;
  }
  
  .videodiv{
    padding: 10px;
    border: 2px solid #282860;
    border-radius: 10px;
  }
  .align-center{
    text-align: center;
  }
  
  @media (min-width: 1024px) {
    header {
      display: flex;
      place-items: center;
      padding-right: calc(var(--section-gap) / 2);
    }
  
    .logo {
      margin: 0 2rem 0 0;
    }
  
    header .wrapper {
      display: flex;
      place-items: flex-start;
      flex-wrap: wrap;
    }
}

.app-header {
    background-color: #9bc6db !important;
}

.video-ctrl-btn {
    width: 20%;
    margin-left: 1rem;
}
.video-card-head {
    display: flex;
    justify-content: space-between;
}
</style>

<script>
import axios from 'axios';
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
import CustomLoader from './components/CustomLoader.vue';
const apiBaseUrl = "http://localhost:5000";

export default {
    data() {
        return {
            originalvideos: [],
            videos: [],
            loading: false,
            videoToRender: null,
            uploadprogress: 0
        };
    },
    methods: {
        setRenderVideo: function (video, isVideoObj = true) {
            console.log("setRenderVideo called with ", video);
            if (!isVideoObj) {
                this.videoToRender = video;
                return;
            }
            this.videoToRender = this.videos[video].file;
        },
        reloadOriginalVideo: function (videoID) {
            this.videos[videoID] = {
                name: this.originalvideos[videoID].name,
                file: this.originalvideos[videoID].file
            };
            this.setRenderVideo(videoID);
        },
        removeVideo: function (videoID) {
            // permanently removes the video
            this.videos.splice(videoID, 1);
            this.originalvideos.splice(videoID, 1);
        },
        editVideoSubmit: function (videoID, actiontype) {
            this.loading = true;
            let video = this.videos[videoID].file;
            if (video === undefined) {
                toast.error("Video is empty!");
                return;
            }
            let editor_payload = {};
            if (actiontype == "trim") {
                editor_payload = {
                    trim_start: document.getElementById("trim_start" + videoID).value,
                    trim_end: document.getElementById("trim_end" + videoID).value
                };
            }
            editor_payload.videofile = video;
            console.log("editor_payload", editor_payload);
            // send edit request to backend and render the preview returned by server
            axios.post("http://localhost:5000/edit_video/" + actiontype, editor_payload).then((res) => {
                this.loading = false;
                if (res.data.status == "success") {
                    this.videos[videoID].file = res.data.edited_videopath;
                    this.setRenderVideo(videoID);
                    toast.success(res.data.message);
                }
                else {
                    toast.error("Video edit failed");
                }
            });
        },
        uploadVideoFile: function () {
            let clipname = document.getElementById("clipname").value;
            let filedata = document.getElementById("fileinput").files[0];
            if (!filedata) {
                toast.warning("File is empty!");
                return;
            }
            if (clipname == "") {
                toast.warning("Clip name is required!");
                return;
            }
            const config = {
                onUploadProgress: progressEvent => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    this.uploadprogress = percentCompleted;
                }
            };
            let data = new FormData();
            data.append("videofile", filedata);
            axios.post(apiBaseUrl + "/upload_video", data, config)
                .then(res => {
                console.log(res);
                this.originalvideos.push({ name: clipname, file: res.data });
                this.videos.push({ name: clipname, file: res.data });
                console.log("videos", this.videos[0]);
                toast.success("Video uploaded!");
                this.setRenderVideo(this.videos.length - 1);
                this.uploadprogress = 0;
            })
                .catch(err => console.log(err));
        },
        finalrender: function () {
            this.loading = true;
            let requestobj = { videoscount: this.videos.length };
            for (let i = 0; i < this.videos.length; i++) {
                requestobj["video" + i] = this.videos[i].file;
            }
            console.log("requestobj", requestobj);
            axios.post(apiBaseUrl + "/merged_render", requestobj).then(res => {
                console.log(res);
                if (res.data.status == "success") {
                    toast.success("Final render success!");
                    this.renderVideo(apiBaseUrl + res.data.finalrender_videopath, false);
                }
                else {
                    toast.error("Final render ERROR: " + res.data.message);
                }
                this.loading = false;
            });
        }
    },
    components: { CustomLoader }
}
</script>
<template>
  <div class="h-screen flex flex-col bg-editor-bg text-gray-200 overflow-hidden">
    <!-- Header Bar -->
    <header
      class="h-12 bg-panel-bg border-b border-panel-border flex items-center justify-between px-4 flex-shrink-0"
    >
      <div class="flex items-center gap-4">
        <h1 class="text-lg font-semibold text-white">Video Editor Online</h1>
      </div>
      <div class="flex items-center gap-2">
        <button
          v-if="videos.length > 0"
          @click="finalrender"
          class="px-4 py-1.5 bg-accent hover:bg-green-600 text-white text-sm font-medium rounded transition-colors"
        >
          <i class="bi bi-download mr-2"></i>Export
        </button>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="flex-1 flex min-h-0">
      <!-- Left Panel: Media Bin -->
      <div class="w-64 bg-panel-bg border-r border-panel-border flex flex-col flex-shrink-0">
        <div class="p-3 border-b border-panel-border">
          <h2 class="text-sm font-medium text-gray-400 uppercase tracking-wide">Media Bin</h2>
        </div>

        <!-- Upload Area -->
        <div class="p-3 border-b border-panel-border">
          <div
            class="border-2 border-dashed border-panel-border rounded-lg p-4 text-center hover:border-gray-500 transition-colors cursor-pointer"
            @click="triggerFileInput"
            @dragover.prevent="dragOver = true"
            @dragleave="dragOver = false"
            @drop.prevent="handleFileDrop"
            :class="{ 'border-accent bg-accent/10': dragOver }"
          >
            <i class="bi bi-cloud-upload text-2xl text-gray-500 mb-2"></i>
            <p class="text-xs text-gray-500">Drop files or click to upload</p>
            <input
              ref="fileInput"
              type="file"
              accept="video/*"
              class="hidden"
              @change="handleFileSelect"
            />
          </div>
          <input
            v-model="clipName"
            type="text"
            placeholder="Clip name..."
            class="w-full mt-2 px-3 py-1.5 bg-editor-bg border border-panel-border rounded text-sm focus:outline-none focus:border-gray-500"
          />
        </div>

        <!-- Clips List -->
        <div class="flex-1 overflow-y-auto p-2">
          <div
            v-for="(video, index) in videos"
            :key="index"
            class="group flex items-center gap-2 p-2 rounded cursor-grab hover:bg-panel-border/50 mb-1"
            :class="{ 'bg-clip-color/20 border border-clip-color/50': selectedClipIndex === index }"
            draggable="true"
            @dragstart="onClipDragStart($event, index)"
            @click="selectClip(index)"
          >
            <!-- Thumbnail placeholder -->
            <div
              class="w-12 h-8 bg-gray-700 rounded flex items-center justify-center flex-shrink-0"
            >
              <i class="bi bi-film text-gray-500 text-xs"></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm truncate">{{ video.name }}</p>
              <p class="text-xs text-gray-500">{{ formatDuration(video.duration) }}</p>
            </div>
            <button
              @click.stop="removeVideo(index)"
              class="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
            >
              <i class="bi bi-trash text-xs"></i>
            </button>
          </div>

          <div v-if="videos.length === 0" class="text-center text-gray-600 text-sm py-8">
            No clips imported
          </div>
        </div>
      </div>

      <!-- Center: Preview -->
      <div class="flex-1 flex flex-col min-w-0">
        <div class="p-3 border-b border-panel-border bg-panel-bg">
          <h2 class="text-sm font-medium text-gray-400 uppercase tracking-wide">Preview</h2>
        </div>
        <div class="flex-1 flex items-center justify-center bg-black p-4">
          <div v-if="videoToRender" class="relative w-full max-w-3xl">
            <video
              ref="videoPlayer"
              :src="apiBaseUrl + '/' + videoToRender"
              controls
              class="w-full h-auto max-h-[50vh] bg-black"
              @timeupdate="onVideoTimeUpdate"
              @loadedmetadata="onPreviewVideoLoaded"
            ></video>
          </div>
          <div v-else class="text-gray-600 text-center">
            <i class="bi bi-play-circle text-6xl mb-4 block"></i>
            <p>Select a clip to preview</p>
          </div>
        </div>
      </div>

      <!-- Right Panel: Properties -->
      <div class="w-72 bg-panel-bg border-l border-panel-border flex flex-col flex-shrink-0">
        <div class="p-3 border-b border-panel-border">
          <h2 class="text-sm font-medium text-gray-400 uppercase tracking-wide">Properties</h2>
        </div>

        <div
          v-if="selectedClipIndex !== null && videos[selectedClipIndex]"
          class="flex-1 overflow-y-auto p-3"
        >
          <div class="space-y-4">
            <!-- Clip Info -->
            <div>
              <label class="text-xs text-gray-500 uppercase">Selected Clip</label>
              <p class="text-sm font-medium">{{ videos[selectedClipIndex].name }}</p>
            </div>

            <!-- Trim Controls -->
            <div class="bg-editor-bg rounded-lg p-3">
              <h3 class="text-sm font-medium mb-3 flex items-center gap-2">
                <i class="bi bi-scissors"></i> Trim
              </h3>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-xs text-gray-500">Start (s)</label>
                  <input
                    type="number"
                    :id="'trim_start' + selectedClipIndex"
                    min="0"
                    :value="videos[selectedClipIndex].trimStart || 0"
                    class="w-full px-2 py-1 bg-panel-bg border border-panel-border rounded text-sm focus:outline-none focus:border-gray-500"
                  />
                </div>
                <div>
                  <label class="text-xs text-gray-500">End (s)</label>
                  <input
                    type="number"
                    :id="'trim_end' + selectedClipIndex"
                    min="0"
                    :value="
                      videos[selectedClipIndex].trimEnd || videos[selectedClipIndex].duration || 0
                    "
                    class="w-full px-2 py-1 bg-panel-bg border border-panel-border rounded text-sm focus:outline-none focus:border-gray-500"
                  />
                </div>
              </div>
              <button
                @click="editVideoSubmit(selectedClipIndex, 'trim')"
                class="w-full mt-3 px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-sm rounded transition-colors"
              >
                Apply Trim
              </button>
            </div>

            <!-- Actions -->
            <div class="space-y-2">
              <button
                @click="reloadOriginalVideo(selectedClipIndex)"
                class="w-full px-3 py-1.5 bg-panel-border hover:bg-gray-600 text-sm rounded transition-colors"
              >
                <i class="bi bi-arrow-counterclockwise mr-2"></i>Reset to Original
              </button>
              <button
                @click="setRenderVideo(selectedClipIndex)"
                class="w-full px-3 py-1.5 bg-clip-color hover:bg-clip-hover text-white text-sm rounded transition-colors"
              >
                <i class="bi bi-eye mr-2"></i>Preview Clip
              </button>
            </div>
          </div>
        </div>

        <div v-else class="flex-1 flex items-center justify-center text-gray-600 text-sm">
          Select a clip to edit
        </div>
      </div>
    </div>

    <!-- Timeline (Fixed Bottom) -->
    <div class="h-48 bg-timeline-bg border-t border-panel-border flex flex-col flex-shrink-0">
      <!-- Timeline Header -->
      <div
        class="h-10 bg-panel-bg border-b border-panel-border flex items-center justify-between px-4 flex-shrink-0"
      >
        <div class="flex items-center gap-4">
          <h2 class="text-sm font-medium">Timeline</h2>
          <div class="flex items-center gap-1 text-xs text-gray-500">
            <span>{{ formatDuration(currentTime) }}</span>
            <span>/</span>
            <span>{{ formatDuration(totalDuration) }}</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="zoomOut"
            class="p-1 hover:bg-panel-border rounded"
            :disabled="zoom <= 0.5"
          >
            <i class="bi bi-zoom-out"></i>
          </button>
          <span class="text-xs text-gray-500 w-12 text-center">{{ Math.round(zoom * 100) }}%</span>
          <button @click="zoomIn" class="p-1 hover:bg-panel-border rounded" :disabled="zoom >= 3">
            <i class="bi bi-zoom-in"></i>
          </button>
        </div>
      </div>

      <!-- Timeline Content -->
      <div
        ref="timelineContainer"
        class="flex-1 overflow-x-auto overflow-y-hidden relative"
        @dragover.prevent
        @drop.prevent="onTimelineDrop"
      >
        <!-- Time Ruler -->
        <div
          class="h-6 bg-panel-bg border-b border-panel-border relative"
          :style="{ width: timelineWidth + 'px', minWidth: '100%' }"
        >
          <div
            v-for="marker in timeMarkers"
            :key="marker.time"
            class="absolute top-0 h-full border-l border-panel-border"
            :style="{ left: marker.position + 'px' }"
          >
            <span class="absolute top-1 left-1 text-[10px] text-gray-500">{{
              formatDuration(marker.time)
            }}</span>
          </div>
        </div>

        <!-- Playhead -->
        <div
          class="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20 cursor-ew-resize"
          :style="{ left: playheadPosition + 'px' }"
          @mousedown="startPlayheadDrag"
        >
          <div
            class="absolute -top-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-red-500 rounded-full"
          ></div>
        </div>

        <!-- Tracks -->
        <div class="relative h-24" :style="{ width: timelineWidth + 'px', minWidth: '100%' }">
          <!-- Video Track -->
          <div class="absolute top-2 left-0 right-0 h-16 flex items-center">
            <div
              v-for="(clip, index) in timelineClips"
              :key="index"
              class="absolute h-14 rounded cursor-pointer transition-all group"
              :class="[
                selectedClipIndex === index
                  ? 'ring-2 ring-white ring-offset-1 ring-offset-timeline-bg'
                  : 'hover:brightness-110',
                'bg-gradient-to-b from-clip-color to-indigo-700'
              ]"
              :style="getClipStyle(clip, index)"
              @click="selectClip(index)"
              draggable="true"
              @dragstart="onTimelineClipDragStart($event, index)"
            >
              <!-- Trim handles -->
              <div
                class="absolute left-0 top-0 bottom-0 w-2 bg-white/20 cursor-ew-resize opacity-0 group-hover:opacity-100 rounded-l"
                @mousedown.stop="startTrim($event, index, 'left')"
              ></div>
              <div
                class="absolute right-0 top-0 bottom-0 w-2 bg-white/20 cursor-ew-resize opacity-0 group-hover:opacity-100 rounded-r"
                @mousedown.stop="startTrim($event, index, 'right')"
              ></div>

              <!-- Clip content -->
              <div class="px-3 py-1 overflow-hidden h-full flex flex-col justify-center">
                <p class="text-xs font-medium truncate text-white">{{ clip.name }}</p>
                <p class="text-[10px] text-white/70">{{ formatDuration(getClipDuration(clip)) }}</p>
              </div>
            </div>
          </div>

          <!-- Drop zone indicator -->
          <div
            v-if="videos.length === 0"
            class="absolute inset-0 flex items-center justify-center text-gray-600 text-sm border-2 border-dashed border-panel-border rounded m-2"
          >
            <i class="bi bi-plus-circle mr-2"></i>
            Drag clips here from Media Bin
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div class="text-center">
        <div
          class="w-12 h-12 border-4 border-clip-color border-t-transparent rounded-full animate-spin mx-auto mb-4"
        ></div>
        <p class="text-gray-300">Processing video...</p>
      </div>
    </div>

    <!-- Upload Progress -->
    <div
      v-if="uploadprogress > 0 && uploadprogress < 100"
      class="fixed bottom-52 left-4 right-4 bg-panel-bg rounded-lg p-3 z-40"
    >
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm">Uploading...</span>
        <span class="text-sm text-gray-400">{{ uploadprogress }}%</span>
      </div>
      <div class="h-2 bg-editor-bg rounded-full overflow-hidden">
        <div class="h-full bg-accent transition-all" :style="{ width: uploadprogress + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { toast } from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export default {
  data() {
    return {
      apiBaseUrl: API_BASE_URL,
      originalvideos: [],
      videos: [],
      loading: false,
      videoToRender: null,
      uploadprogress: 0,
      currentTime: 0,
      selectedClipIndex: null,
      clipName: '',
      dragOver: false,
      zoom: 1,
      pixelsPerSecond: 50,
      trimming: null,
      playheadDragging: false,
      dragStartX: 0,
      dragStartValue: 0
    }
  },
  computed: {
    timelineClips() {
      return this.videos.map((video) => ({
        name: video.name,
        file: video.file,
        duration: video.duration || 10,
        trimStart: video.trimStart || 0,
        trimEnd: video.trimEnd || video.duration || 10
      }))
    },
    totalDuration() {
      return this.videos.reduce((sum, clip) => {
        const duration = (clip.trimEnd || clip.duration || 10) - (clip.trimStart || 0)
        return sum + duration
      }, 0)
    },
    timelineWidth() {
      return Math.max(this.totalDuration * this.pixelsPerSecond * this.zoom, 800)
    },
    timeMarkers() {
      const markers = []
      const interval = this.zoom >= 1.5 ? 5 : this.zoom >= 0.75 ? 10 : 30
      const maxTime = Math.ceil(Math.max(this.totalDuration, 60) / interval) * interval + interval
      for (let t = 0; t <= maxTime; t += interval) {
        markers.push({
          time: t,
          position: t * this.pixelsPerSecond * this.zoom
        })
      }
      return markers
    },
    playheadPosition() {
      return this.currentTime * this.pixelsPerSecond * this.zoom
    }
  },
  methods: {
    formatDuration(seconds) {
      if (!seconds || !isFinite(seconds)) return '0:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    getClipDuration(clip) {
      return (clip.trimEnd || clip.duration || 10) - (clip.trimStart || 0)
    },
    getClipStyle(clip, index) {
      let left = 0
      for (let i = 0; i < index; i++) {
        left += this.getClipDuration(this.timelineClips[i])
      }
      const width = this.getClipDuration(clip)
      return {
        left: left * this.pixelsPerSecond * this.zoom + 'px',
        width: Math.max(width * this.pixelsPerSecond * this.zoom, 40) + 'px'
      }
    },
    zoomIn() {
      this.zoom = Math.min(this.zoom + 0.25, 3)
    },
    zoomOut() {
      this.zoom = Math.max(this.zoom - 0.25, 0.5)
    },
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) this.uploadFile(file)
    },
    handleFileDrop(event) {
      this.dragOver = false
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('video/')) {
        this.uploadFile(file)
      }
    },
    uploadFile(file) {
      if (!this.clipName.trim()) {
        this.clipName = file.name.replace(/\.[^/.]+$/, '')
      }

      const config = {
        onUploadProgress: (progressEvent) => {
          this.uploadprogress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      }

      const data = new FormData()
      data.append('videofile', file)

      axios
        .post(this.apiBaseUrl + '/upload_video', data, config)
        .then((res) => {
          const newIndex = this.videos.length
          this.originalvideos.push({ name: this.clipName, file: res.data, duration: null })
          this.videos.push({ name: this.clipName, file: res.data, duration: null })
          toast.success('Clip imported!')
          this.selectedClipIndex = newIndex
          this.setRenderVideo(newIndex)
          this.uploadprogress = 0
          this.clipName = ''
          this.$refs.fileInput.value = ''
        })
        .catch((err) => {
          this.uploadprogress = 0
          const message = err.response?.data?.message || err.message || 'Upload failed'
          toast.error(message)
        })
    },
    selectClip(index) {
      this.selectedClipIndex = index
      this.setRenderVideo(index)
    },
    setRenderVideo(video, isVideoObj = true) {
      if (!isVideoObj) {
        this.videoToRender = video
        return
      }
      if (this.videos[video]) {
        this.videoToRender = this.videos[video].file
      }
    },
    removeVideo(index) {
      this.videos.splice(index, 1)
      this.originalvideos.splice(index, 1)
      if (this.selectedClipIndex === index) {
        this.selectedClipIndex = null
        this.videoToRender = null
      } else if (this.selectedClipIndex > index) {
        this.selectedClipIndex--
      }
      toast.info('Clip removed')
    },
    reloadOriginalVideo(videoID) {
      const original = this.originalvideos[videoID]
      this.videos[videoID] = {
        name: original.name,
        file: original.file,
        duration: original.duration,
        trimStart: 0,
        trimEnd: original.duration || 10
      }
      this.setRenderVideo(videoID)
      toast.info('Reset to original')
    },
    editVideoSubmit(videoID, actiontype) {
      this.loading = true
      const video = this.videos[videoID].file

      const editor_payload = {
        videofile: video,
        trim_start: document.getElementById('trim_start' + videoID).value,
        trim_end: document.getElementById('trim_end' + videoID).value
      }

      axios
        .post(this.apiBaseUrl + '/edit_video/' + actiontype, editor_payload)
        .then((res) => {
          this.loading = false
          if (res.data.status === 'success') {
            this.videos[videoID].file = res.data.edited_videopath
            this.setRenderVideo(videoID)
            toast.success('Trim applied!')
          } else {
            toast.error(res.data.message || 'Edit failed')
          }
        })
        .catch((err) => {
          this.loading = false
          toast.error(err.response?.data?.message || 'Edit failed')
        })
    },
    finalrender() {
      this.loading = true
      const requestobj = { videoscount: this.videos.length }
      for (let i = 0; i < this.videos.length; i++) {
        requestobj['video' + i] = this.videos[i].file
      }

      axios
        .post(this.apiBaseUrl + '/merged_render', requestobj)
        .then((res) => {
          if (res.data.status === 'success') {
            toast.success('Export complete!')
            this.setRenderVideo(res.data.finalrender_videopath, false)
          } else {
            toast.error(res.data.message)
          }
          this.loading = false
        })
        .catch((err) => {
          this.loading = false
          toast.error(err.response?.data?.message || 'Export failed')
        })
    },
    onVideoTimeUpdate(e) {
      this.currentTime = e.target.currentTime
    },
    onPreviewVideoLoaded(event) {
      const duration = event.target.duration
      if (duration && isFinite(duration) && this.selectedClipIndex !== null) {
        const idx = this.selectedClipIndex
        if (this.videos[idx]) {
          this.videos[idx].duration = duration
          if (!this.videos[idx].trimEnd) {
            this.videos[idx].trimEnd = duration
          }
          if (this.originalvideos[idx]) {
            this.originalvideos[idx].duration = duration
          }
        }
      }
    },
    // Drag and drop from media bin
    onClipDragStart(event, index) {
      event.dataTransfer.setData('clipIndex', index)
      event.dataTransfer.setData('source', 'mediaBin')
    },
    onTimelineClipDragStart(event, index) {
      event.dataTransfer.setData('clipIndex', index)
      event.dataTransfer.setData('source', 'timeline')
    },
    onTimelineDrop(event) {
      const source = event.dataTransfer.getData('source')
      const clipIndex = parseInt(event.dataTransfer.getData('clipIndex'))

      if (source === 'timeline' && !isNaN(clipIndex)) {
        // Reorder clips
        const container = this.$refs.timelineContainer
        const rect = container.getBoundingClientRect()
        const x = event.clientX - rect.left + container.scrollLeft

        let accumulatedWidth = 0
        let newIndex = this.videos.length - 1

        for (let i = 0; i < this.videos.length; i++) {
          const clipWidth =
            this.getClipDuration(this.timelineClips[i]) * this.pixelsPerSecond * this.zoom
          if (x < accumulatedWidth + clipWidth / 2) {
            newIndex = i
            break
          }
          accumulatedWidth += clipWidth
        }

        if (newIndex !== clipIndex) {
          const [movedVideo] = this.videos.splice(clipIndex, 1)
          this.videos.splice(newIndex, 0, movedVideo)
          const [movedOriginal] = this.originalvideos.splice(clipIndex, 1)
          this.originalvideos.splice(newIndex, 0, movedOriginal)
          this.selectedClipIndex = newIndex
          toast.info(`Moved to position ${newIndex + 1}`)
        }
      }
    },
    // Timeline trim handles
    startTrim(e, index, side) {
      this.trimming = { index, side }
      this.dragStartX = e.clientX
      const clip = this.videos[index]
      this.dragStartValue =
        side === 'left' ? clip.trimStart || 0 : clip.trimEnd || clip.duration || 10
      document.addEventListener('mousemove', this.onTrim)
      document.addEventListener('mouseup', this.stopTrim)
    },
    onTrim(e) {
      if (!this.trimming) return
      const deltaX = e.clientX - this.dragStartX
      const deltaTime = deltaX / (this.pixelsPerSecond * this.zoom)
      const clip = this.videos[this.trimming.index]
      const duration = clip.duration || 10

      if (this.trimming.side === 'left') {
        const newStart = Math.max(
          0,
          Math.min(this.dragStartValue + deltaTime, (clip.trimEnd || duration) - 1)
        )
        this.videos[this.trimming.index].trimStart = newStart
      } else {
        const newEnd = Math.max(
          (clip.trimStart || 0) + 1,
          Math.min(this.dragStartValue + deltaTime, duration)
        )
        this.videos[this.trimming.index].trimEnd = newEnd
      }
    },
    stopTrim() {
      this.trimming = null
      document.removeEventListener('mousemove', this.onTrim)
      document.removeEventListener('mouseup', this.stopTrim)
    },
    // Playhead
    startPlayheadDrag(e) {
      this.playheadDragging = true
      document.addEventListener('mousemove', this.onPlayheadDrag)
      document.addEventListener('mouseup', this.stopPlayheadDrag)
    },
    onPlayheadDrag(e) {
      if (!this.playheadDragging) return
      const container = this.$refs.timelineContainer
      const rect = container.getBoundingClientRect()
      const x = Math.max(0, e.clientX - rect.left + container.scrollLeft)
      const time = x / (this.pixelsPerSecond * this.zoom)
      this.currentTime = Math.min(time, this.totalDuration)
      if (this.$refs.videoPlayer) {
        this.$refs.videoPlayer.currentTime = this.currentTime
      }
    },
    stopPlayheadDrag() {
      this.playheadDragging = false
      document.removeEventListener('mousemove', this.onPlayheadDrag)
      document.removeEventListener('mouseup', this.stopPlayheadDrag)
    }
  }
}
</script>

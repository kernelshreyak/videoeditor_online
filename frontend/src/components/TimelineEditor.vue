<template>
    <div class="timeline-editor" v-if="clips.length > 0">
        <div class="timeline-header">
            <h4>Timeline</h4>
            <div class="timeline-controls">
                <button class="btn btn-sm btn-outline-secondary" @click="zoomOut" :disabled="zoom <= 0.5">
                    <i class="bi bi-zoom-out"></i> -
                </button>
                <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
                <button class="btn btn-sm btn-outline-secondary" @click="zoomIn" :disabled="zoom >= 3">
                    <i class="bi bi-zoom-in"></i> +
                </button>
            </div>
        </div>

        <div class="timeline-container" ref="timelineContainer">
            <!-- Time ruler -->
            <div class="time-ruler" :style="{ width: timelineWidth + 'px' }">
                <div v-for="marker in timeMarkers" :key="marker.time"
                     class="time-marker"
                     :style="{ left: marker.position + 'px' }">
                    <span class="time-label">{{ formatTime(marker.time) }}</span>
                </div>
            </div>

            <!-- Playhead -->
            <div class="playhead"
                 :style="{ left: playheadPosition + 'px' }"
                 @mousedown="startPlayheadDrag">
                <div class="playhead-handle"></div>
                <div class="playhead-line"></div>
            </div>

            <!-- Clips track -->
            <div class="clips-track" :style="{ width: timelineWidth + 'px' }">
                <div v-for="(clip, index) in clips"
                     :key="index"
                     class="timeline-clip"
                     :class="{ 'selected': selectedClip === index, 'dragging': draggingClip === index }"
                     :style="getClipStyle(clip, index)"
                     @mousedown="(e) => startClipDrag(e, index)"
                     @click="selectClip(index)">

                    <!-- Left trim handle -->
                    <div class="trim-handle trim-handle-left"
                         @mousedown.stop="(e) => startTrim(e, index, 'left')">
                    </div>

                    <!-- Clip content -->
                    <div class="clip-content">
                        <span class="clip-name">{{ clip.name }}</span>
                        <span class="clip-duration">{{ formatTime(getClipDuration(clip)) }}</span>
                    </div>

                    <!-- Right trim handle -->
                    <div class="trim-handle trim-handle-right"
                         @mousedown.stop="(e) => startTrim(e, index, 'right')">
                    </div>
                </div>
            </div>
        </div>

        <!-- Selected clip info -->
        <div class="clip-info" v-if="selectedClip !== null && clips[selectedClip]">
            <div class="clip-info-row">
                <span><strong>Selected:</strong> {{ clips[selectedClip].name }}</span>
                <span><strong>Start:</strong> {{ formatTime(clips[selectedClip].trimStart || 0) }}</span>
                <span><strong>End:</strong> {{ formatTime(clips[selectedClip].trimEnd || clips[selectedClip].duration || 10) }}</span>
            </div>
            <div class="clip-actions">
                <button class="btn btn-sm btn-outline-primary" @click="moveClipLeft" :disabled="selectedClip === 0">
                    <i class="bi bi-arrow-left"></i> Move Left
                </button>
                <button class="btn btn-sm btn-outline-primary" @click="moveClipRight" :disabled="selectedClip === clips.length - 1">
                    Move Right <i class="bi bi-arrow-right"></i>
                </button>
            </div>
        </div>
    </div>
    <div v-else class="timeline-empty">
        <p>Upload clips to see the timeline</p>
    </div>
</template>

<script>
export default {
    name: "TimelineEditor",
    props: {
        clips: {
            type: Array,
            default: () => []
        },
        currentTime: {
            type: Number,
            default: 0
        }
    },
    emits: ['clip-selected', 'clip-reorder', 'clip-trim', 'seek'],
    data() {
        return {
            zoom: 1,
            pixelsPerSecond: 50,
            selectedClip: null,
            draggingClip: null,
            trimming: null,
            playheadDragging: false,
            dragStartX: 0,
            dragStartValue: 0
        };
    },
    computed: {
        totalDuration() {
            return this.clips.reduce((sum, clip) => {
                const duration = (clip.trimEnd || clip.duration || 10) - (clip.trimStart || 0);
                return sum + duration;
            }, 0);
        },
        timelineWidth() {
            return Math.max(this.totalDuration * this.pixelsPerSecond * this.zoom, 600);
        },
        timeMarkers() {
            const markers = [];
            const interval = this.zoom >= 1.5 ? 5 : this.zoom >= 0.75 ? 10 : 30;
            const maxTime = Math.ceil(this.totalDuration / interval) * interval + interval;
            for (let t = 0; t <= maxTime; t += interval) {
                markers.push({
                    time: t,
                    position: t * this.pixelsPerSecond * this.zoom
                });
            }
            return markers;
        },
        playheadPosition() {
            return this.currentTime * this.pixelsPerSecond * this.zoom;
        }
    },
    methods: {
        formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        },
        getClipDuration(clip) {
            return (clip.trimEnd || clip.duration || 10) - (clip.trimStart || 0);
        },
        getClipStyle(clip, index) {
            let left = 0;
            for (let i = 0; i < index; i++) {
                left += this.getClipDuration(this.clips[i]);
            }
            const width = this.getClipDuration(clip);
            return {
                left: (left * this.pixelsPerSecond * this.zoom) + 'px',
                width: (width * this.pixelsPerSecond * this.zoom) + 'px'
            };
        },
        zoomIn() {
            this.zoom = Math.min(this.zoom + 0.25, 3);
        },
        zoomOut() {
            this.zoom = Math.max(this.zoom - 0.25, 0.5);
        },
        selectClip(index) {
            this.selectedClip = index;
            this.$emit('clip-selected', index);
        },
        moveClipLeft() {
            if (this.selectedClip > 0) {
                this.$emit('clip-reorder', this.selectedClip, this.selectedClip - 1);
                this.selectedClip--;
            }
        },
        moveClipRight() {
            if (this.selectedClip < this.clips.length - 1) {
                this.$emit('clip-reorder', this.selectedClip, this.selectedClip + 1);
                this.selectedClip++;
            }
        },
        startClipDrag(e, index) {
            if (e.target.classList.contains('trim-handle-left') ||
                e.target.classList.contains('trim-handle-right')) {
                return;
            }
            this.draggingClip = index;
            this.dragStartX = e.clientX;
            document.addEventListener('mousemove', this.onClipDrag);
            document.addEventListener('mouseup', this.stopClipDrag);
        },
        onClipDrag(e) {
            // Visual feedback only - actual reorder on drop
        },
        stopClipDrag(e) {
            if (this.draggingClip !== null) {
                const container = this.$refs.timelineContainer;
                const rect = container.getBoundingClientRect();
                const x = e.clientX - rect.left + container.scrollLeft;

                // Calculate which position the clip should move to
                let accumulatedWidth = 0;
                let newIndex = this.clips.length - 1;

                for (let i = 0; i < this.clips.length; i++) {
                    const clipWidth = this.getClipDuration(this.clips[i]) * this.pixelsPerSecond * this.zoom;
                    if (x < accumulatedWidth + clipWidth / 2) {
                        newIndex = i;
                        break;
                    }
                    accumulatedWidth += clipWidth;
                }

                if (newIndex !== this.draggingClip) {
                    this.$emit('clip-reorder', this.draggingClip, newIndex);
                    this.selectedClip = newIndex;
                }
            }
            this.draggingClip = null;
            document.removeEventListener('mousemove', this.onClipDrag);
            document.removeEventListener('mouseup', this.stopClipDrag);
        },
        startTrim(e, index, side) {
            this.trimming = { index, side };
            this.dragStartX = e.clientX;
            const clip = this.clips[index];
            this.dragStartValue = side === 'left' ? (clip.trimStart || 0) : (clip.trimEnd || clip.duration || 10);
            document.addEventListener('mousemove', this.onTrim);
            document.addEventListener('mouseup', this.stopTrim);
        },
        onTrim(e) {
            if (!this.trimming) return;
            const deltaX = e.clientX - this.dragStartX;
            const deltaTime = deltaX / (this.pixelsPerSecond * this.zoom);
            const clip = this.clips[this.trimming.index];
            const duration = clip.duration || 10;

            if (this.trimming.side === 'left') {
                const newStart = Math.max(0, Math.min(this.dragStartValue + deltaTime, (clip.trimEnd || duration) - 1));
                this.$emit('clip-trim', this.trimming.index, newStart, clip.trimEnd || duration);
            } else {
                const newEnd = Math.max((clip.trimStart || 0) + 1, Math.min(this.dragStartValue + deltaTime, duration));
                this.$emit('clip-trim', this.trimming.index, clip.trimStart || 0, newEnd);
            }
        },
        stopTrim() {
            this.trimming = null;
            document.removeEventListener('mousemove', this.onTrim);
            document.removeEventListener('mouseup', this.stopTrim);
        },
        startPlayheadDrag(e) {
            this.playheadDragging = true;
            document.addEventListener('mousemove', this.onPlayheadDrag);
            document.addEventListener('mouseup', this.stopPlayheadDrag);
        },
        onPlayheadDrag(e) {
            if (!this.playheadDragging) return;
            const container = this.$refs.timelineContainer;
            const rect = container.getBoundingClientRect();
            const x = Math.max(0, e.clientX - rect.left + container.scrollLeft);
            const time = x / (this.pixelsPerSecond * this.zoom);
            this.$emit('seek', Math.min(time, this.totalDuration));
        },
        stopPlayheadDrag() {
            this.playheadDragging = false;
            document.removeEventListener('mousemove', this.onPlayheadDrag);
            document.removeEventListener('mouseup', this.stopPlayheadDrag);
        }
    }
}
</script>

<style scoped>
.timeline-editor {
    background: #1a1a2e;
    border-radius: 8px;
    padding: 15px;
    margin-top: 20px;
}

.timeline-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.timeline-header h4 {
    color: #fff;
    margin: 0;
}

.timeline-controls {
    display: flex;
    align-items: center;
    gap: 10px;
}

.timeline-controls .btn {
    color: #fff;
    border-color: #444;
}

.zoom-level {
    color: #aaa;
    min-width: 50px;
    text-align: center;
}

.timeline-container {
    position: relative;
    overflow-x: auto;
    background: #16213e;
    border-radius: 4px;
    min-height: 120px;
    padding-top: 25px;
}

.time-ruler {
    position: absolute;
    top: 0;
    left: 0;
    height: 25px;
    background: #0f3460;
}

.time-marker {
    position: absolute;
    top: 0;
    height: 100%;
    border-left: 1px solid #444;
}

.time-label {
    position: absolute;
    top: 5px;
    left: 5px;
    font-size: 10px;
    color: #888;
    white-space: nowrap;
}

.playhead {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    z-index: 10;
    cursor: ew-resize;
}

.playhead-handle {
    width: 12px;
    height: 12px;
    background: #e94560;
    border-radius: 50%;
    position: absolute;
    top: 6px;
    left: -5px;
}

.playhead-line {
    width: 2px;
    height: 100%;
    background: #e94560;
    position: absolute;
    top: 0;
    left: 0;
}

.clips-track {
    position: relative;
    min-height: 80px;
    padding: 10px 0;
}

.timeline-clip {
    position: absolute;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    cursor: grab;
    display: flex;
    align-items: center;
    overflow: hidden;
    transition: transform 0.1s, box-shadow 0.1s;
    border: 2px solid transparent;
}

.timeline-clip:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.timeline-clip.selected {
    border-color: #fff;
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

.timeline-clip.dragging {
    opacity: 0.7;
    cursor: grabbing;
}

.trim-handle {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 10px;
    background: rgba(255, 255, 255, 0.3);
    cursor: ew-resize;
    opacity: 0;
    transition: opacity 0.2s;
}

.timeline-clip:hover .trim-handle {
    opacity: 1;
}

.trim-handle-left {
    left: 0;
    border-radius: 4px 0 0 4px;
}

.trim-handle-right {
    right: 0;
    border-radius: 0 4px 4px 0;
}

.clip-content {
    flex: 1;
    padding: 0 15px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.clip-name {
    color: #fff;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.clip-duration {
    color: rgba(255, 255, 255, 0.7);
    font-size: 11px;
}

.clip-info {
    margin-top: 15px;
    padding: 10px;
    background: #0f3460;
    border-radius: 4px;
}

.clip-info-row {
    display: flex;
    gap: 20px;
    color: #fff;
    margin-bottom: 10px;
}

.clip-actions {
    display: flex;
    gap: 10px;
}

.timeline-empty {
    background: #1a1a2e;
    border-radius: 8px;
    padding: 30px;
    text-align: center;
    color: #888;
    margin-top: 20px;
}
</style>

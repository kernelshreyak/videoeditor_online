<template>
    <div class="timeline-edtitor">
        <h3>Timeline Editor</h3>
        <div id="timeline">
            <div class="marker" style="left: 20%;"></div>
            <div class="marker" style="left: 40%;"></div>
            <div class="marker" style="left: 60%;"></div>
        </div>
        <br>
        <!-- <video controls>
            <source src="sample.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video> -->
        </div>

</template>

<style scoped>
    #timeline {
        width: 80%;
        height: 100px;
        background-color: #f0f0f0;
        position: relative;
    }

    .marker {
        width: 2px;
        height: 100%;
        background-color: red;
        position: absolute;
        cursor: pointer;
    }

    video {
        width: 100%;
    }    
</style>

<script>
    export default {
        name: "TimelineEditor",
    }
</script>
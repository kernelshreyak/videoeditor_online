"""
Comprehensive tests for video editor backend.

Tests cover:
- Flask API routes (health check, upload, edit, merge)
- video_utils functions (trim_video, merge_videos)
- Error handling and edge cases
"""

import io
import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from backend import create_app
from backend.config import BASE_DIR, CLIPS_DIR
from backend.video_utils import (
    ensure_clips_dir,
    merge_videos,
    trim_video,
    _relative_clip_path,
    _resolve_clip_path,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def mock_clips_dir(tmp_path, monkeypatch):
    """Create a temporary clips directory for testing."""
    clips_dir = tmp_path / "clips"
    clips_dir.mkdir()
    monkeypatch.setattr("backend.video_utils.CLIPS_DIR", clips_dir)
    monkeypatch.setattr("backend.CLIPS_DIR", clips_dir)
    return clips_dir


@pytest.fixture
def mock_base_dir(tmp_path, monkeypatch):
    """Mock BASE_DIR for testing."""
    monkeypatch.setattr("backend.video_utils.BASE_DIR", tmp_path)
    monkeypatch.setattr("backend.config.BASE_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def mock_video_clip():
    """Create a mock VideoFileClip."""
    mock_clip = MagicMock()
    mock_clip.subclip = MagicMock(return_value=mock_clip)
    mock_clip.write_videofile = MagicMock()
    mock_clip.close = MagicMock()
    mock_clip.duration = 10.0
    return mock_clip


# ============================================================================
# API ROUTE TESTS
# ============================================================================


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_success(self, client):
        """Test that health endpoint returns success."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "success"
        assert data["message"] == "Video editor backend"


class TestClipsEndpoint:
    """Tests for the clips serving endpoint."""

    def test_render_clip_success(self, client, mock_clips_dir):
        """Test serving an existing clip file."""
        # Create a test file
        test_file = mock_clips_dir / "test_video.mp4"
        test_file.write_text("fake video content")

        response = client.get("/clips/test_video.mp4")
        assert response.status_code == 200

    def test_render_clip_not_found(self, client, mock_clips_dir):
        """Test handling of missing clip file."""
        response = client.get("/clips/nonexistent.mp4")
        assert response.status_code == 404

        data = response.get_json()
        assert data["status"] == "error"
        assert data["message"] == "File not found"


class TestUploadEndpoint:
    """Tests for the video upload endpoint."""

    def test_upload_video_success(self, client, mock_clips_dir):
        """Test successful video upload."""
        data = {
            "videofile": (io.BytesIO(b"fake video data"), "test_upload.mp4")
        }

        response = client.post(
            "/upload_video",
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 200
        assert "clips/test_upload.mp4" in response.get_data(as_text=True)

        # Verify file was saved
        uploaded_file = mock_clips_dir / "test_upload.mp4"
        assert uploaded_file.exists()

    def test_upload_video_no_file(self, client):
        """Test upload with no file provided."""
        response = client.post("/upload_video", data={})
        assert response.status_code == 400

        data = response.get_json()
        assert data["status"] == "error"
        assert "No video file provided" in data["message"]

    def test_upload_video_empty_filename(self, client):
        """Test upload with empty filename."""
        data = {
            "videofile": (io.BytesIO(b"data"), "")
        }

        response = client.post(
            "/upload_video",
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"

    def test_upload_video_secure_filename(self, client, mock_clips_dir):
        """Test that filenames are sanitized using secure_filename."""
        data = {
            "videofile": (io.BytesIO(b"data"), "../../evil/path/hack.mp4")
        }

        response = client.post(
            "/upload_video",
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 200
        # Secure filename should remove path traversal attempts
        response_text = response.get_data(as_text=True)
        assert ".." not in response_text


class TestEditVideoEndpoint:
    """Tests for the video editing endpoint."""

    @patch("backend.trim_video")
    def test_edit_video_trim_success(self, mock_trim, client):
        """Test successful video trimming."""
        mock_trim.return_value = "clips/edited_123_video.mp4"

        payload = {
            "videofile": "clips/original.mp4",
            "trim_start": 5,
            "trim_end": 15
        }

        response = client.post(
            "/edit_video/trim",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["message"] == "video edit success"
        assert data["edited_videopath"] == "clips/edited_123_video.mp4"

        mock_trim.assert_called_once_with("clips/original.mp4", 5, 15)

    def test_edit_video_missing_videofile(self, client):
        """Test editing with missing videofile parameter."""
        payload = {
            "trim_start": 5,
            "trim_end": 15
        }

        response = client.post(
            "/edit_video/trim",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "Missing 'videofile'" in data["message"]

    def test_edit_video_unsupported_action(self, client):
        """Test editing with unsupported action type."""
        payload = {
            "videofile": "clips/test.mp4"
        }

        response = client.post(
            "/edit_video/rotate",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "Unsupported action type" in data["message"]

    @patch("backend.trim_video")
    def test_edit_video_value_error(self, mock_trim, client):
        """Test handling of ValueError from trim_video."""
        mock_trim.side_effect = ValueError("Invalid trim window")

        payload = {
            "videofile": "clips/test.mp4",
            "trim_start": 10,
            "trim_end": 5
        }

        response = client.post(
            "/edit_video/trim",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "Invalid trim window" in data["message"]

    @patch("backend.trim_video")
    def test_edit_video_generic_exception(self, mock_trim, client):
        """Test handling of generic exceptions from trim_video."""
        mock_trim.side_effect = Exception("Processing failed")

        payload = {
            "videofile": "clips/test.mp4",
            "trim_start": 5,
            "trim_end": 15
        }

        response = client.post(
            "/edit_video/trim",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"
        assert "video edit failure" in data["message"]

    def test_edit_video_default_values(self, client):
        """Test that trim_start and trim_end have default values of 0."""
        with patch("backend.trim_video") as mock_trim:
            mock_trim.return_value = "clips/edited.mp4"

            payload = {"videofile": "clips/test.mp4"}

            response = client.post(
                "/edit_video/trim",
                data=json.dumps(payload),
                content_type="application/json"
            )

            assert response.status_code == 200
            mock_trim.assert_called_once_with("clips/test.mp4", 0, 0)


class TestMergedRenderEndpoint:
    """Tests for the video merge endpoint."""

    @patch("backend.merge_videos")
    def test_merged_render_success(self, mock_merge, client):
        """Test successful video merging."""
        mock_merge.return_value = "clips/finalrender_123.mp4"

        payload = {
            "videoscount": 3,
            "video0": "clips/clip1.mp4",
            "video1": "clips/clip2.mp4",
            "video2": "clips/clip3.mp4"
        }

        response = client.post(
            "/merged_render",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["message"] == "merged render success"
        assert data["finalrender_videopath"] == "clips/finalrender_123.mp4"

        expected_clips = ["clips/clip1.mp4", "clips/clip2.mp4", "clips/clip3.mp4"]
        mock_merge.assert_called_once_with(expected_clips)

    def test_merged_render_invalid_count_zero(self, client):
        """Test merge with zero videos count."""
        payload = {"videoscount": 0}

        response = client.post(
            "/merged_render",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "Invalid videos count" in data["message"]

    def test_merged_render_invalid_count_negative(self, client):
        """Test merge with negative videos count."""
        payload = {"videoscount": -1}

        response = client.post(
            "/merged_render",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"

    def test_merged_render_missing_video_path(self, client):
        """Test merge with missing video path."""
        payload = {
            "videoscount": 2,
            "video0": "clips/clip1.mp4"
            # video1 is missing
        }

        response = client.post(
            "/merged_render",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "Missing video1 path" in data["message"]

    def test_merged_render_invalid_count_type(self, client):
        """Test merge with non-integer videoscount."""
        payload = {"videoscount": "invalid"}

        response = client.post(
            "/merged_render",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "videoscount must be an integer" in data["message"]

    @patch("backend.merge_videos")
    def test_merged_render_file_not_found(self, mock_merge, client):
        """Test merge with missing video file."""
        mock_merge.side_effect = FileNotFoundError("Video not found: clips/missing.mp4")

        payload = {
            "videoscount": 1,
            "video0": "clips/missing.mp4"
        }

        response = client.post(
            "/merged_render",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "error"

    @patch("backend.merge_videos")
    def test_merged_render_generic_exception(self, mock_merge, client):
        """Test merge with generic exception."""
        mock_merge.side_effect = Exception("Merge processing failed")

        payload = {
            "videoscount": 1,
            "video0": "clips/test.mp4"
        }

        response = client.post(
            "/merged_render",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"
        assert "video merge failure" in data["message"]


# ============================================================================
# VIDEO UTILS UNIT TESTS
# ============================================================================


class TestEnsureClipsDir:
    """Tests for ensure_clips_dir function."""

    def test_ensure_clips_dir_creates_directory(self, tmp_path, monkeypatch):
        """Test that ensure_clips_dir creates the directory if it doesn't exist."""
        clips_dir = tmp_path / "new_clips"
        monkeypatch.setattr("backend.video_utils.CLIPS_DIR", clips_dir)

        assert not clips_dir.exists()
        ensure_clips_dir()
        assert clips_dir.exists()
        assert clips_dir.is_dir()

    def test_ensure_clips_dir_existing_directory(self, tmp_path, monkeypatch):
        """Test that ensure_clips_dir works when directory already exists."""
        clips_dir = tmp_path / "existing_clips"
        clips_dir.mkdir()
        monkeypatch.setattr("backend.video_utils.CLIPS_DIR", clips_dir)

        # Should not raise an error
        ensure_clips_dir()
        assert clips_dir.exists()


class TestResolveClipPath:
    """Tests for _resolve_clip_path function."""

    def test_resolve_absolute_path(self):
        """Test that absolute paths are returned as-is."""
        abs_path = "/absolute/path/to/video.mp4"
        result = _resolve_clip_path(abs_path)
        assert result == Path(abs_path)

    def test_resolve_relative_path(self, tmp_path, monkeypatch):
        """Test that relative paths are resolved against BASE_DIR."""
        monkeypatch.setattr("backend.video_utils.BASE_DIR", tmp_path)

        relative_path = "clips/video.mp4"
        result = _resolve_clip_path(relative_path)

        expected = (tmp_path / relative_path).resolve()
        assert result == expected


class TestRelativeClipPath:
    """Tests for _relative_clip_path function."""

    def test_relative_clip_path_inside_base(self, tmp_path, monkeypatch):
        """Test conversion of path inside BASE_DIR to relative path."""
        monkeypatch.setattr("backend.video_utils.BASE_DIR", tmp_path)

        clip_path = tmp_path / "clips" / "video.mp4"
        result = _relative_clip_path(clip_path)

        assert result == "clips/video.mp4"

    def test_relative_clip_path_outside_base(self, tmp_path, monkeypatch):
        """Test path outside BASE_DIR returns absolute path as string."""
        monkeypatch.setattr("backend.video_utils.BASE_DIR", tmp_path)

        clip_path = Path("/somewhere/else/video.mp4")
        result = _relative_clip_path(clip_path)

        assert result == str(clip_path)


class TestTrimVideo:
    """Tests for trim_video function."""

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.time.time")
    def test_trim_video_success(
        self, mock_time, mock_video_clip_class, mock_clips_dir, mock_base_dir
    ):
        """Test successful video trimming."""
        mock_time.return_value = 1234567890

        # Create source video file
        source_file = mock_clips_dir / "source.mp4"
        source_file.write_text("fake video")

        # Setup mocks
        mock_clip = MagicMock()
        mock_trimmed = MagicMock()
        mock_clip.subclip.return_value = mock_trimmed
        mock_video_clip_class.return_value = mock_clip

        # Call trim_video
        result = trim_video("clips/source.mp4", 5, 15)

        # Verify calls
        mock_video_clip_class.assert_called_once_with(str(source_file))
        mock_clip.subclip.assert_called_once_with(5, 15)
        mock_trimmed.write_videofile.assert_called_once()
        mock_trimmed.close.assert_called_once()
        mock_clip.close.assert_called_once()

        # Verify result
        assert "edited_1234567890_source.mp4" in result

    def test_trim_video_invalid_start_time(self, mock_clips_dir):
        """Test trim_video with negative start time."""
        with pytest.raises(ValueError, match="Invalid trim window"):
            trim_video("clips/video.mp4", -5, 10)

    def test_trim_video_invalid_time_range(self, mock_clips_dir):
        """Test trim_video with end_time <= start_time."""
        with pytest.raises(ValueError, match="Invalid trim window"):
            trim_video("clips/video.mp4", 10, 5)

    def test_trim_video_equal_times(self, mock_clips_dir):
        """Test trim_video with equal start and end times."""
        with pytest.raises(ValueError, match="Invalid trim window"):
            trim_video("clips/video.mp4", 10, 10)

    def test_trim_video_source_not_found(self, mock_clips_dir, mock_base_dir):
        """Test trim_video with missing source file."""
        with pytest.raises(FileNotFoundError, match="Source video not found"):
            trim_video("clips/nonexistent.mp4", 0, 10)

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.time.time")
    def test_trim_video_creates_clips_dir(
        self, mock_time, mock_video_clip_class, tmp_path, monkeypatch
    ):
        """Test that trim_video creates clips directory if it doesn't exist."""
        mock_time.return_value = 1234567890

        # Setup directories
        clips_dir = tmp_path / "clips"
        monkeypatch.setattr("backend.video_utils.CLIPS_DIR", clips_dir)
        monkeypatch.setattr("backend.video_utils.BASE_DIR", tmp_path)

        # Create source in a different location
        source_file = tmp_path / "source.mp4"
        source_file.write_text("fake video")

        # Setup mocks
        mock_clip = MagicMock()
        mock_trimmed = MagicMock()
        mock_clip.subclip.return_value = mock_trimmed
        mock_video_clip_class.return_value = mock_clip

        assert not clips_dir.exists()

        # Call trim_video with absolute path
        trim_video(str(source_file), 0, 5)

        # Verify clips directory was created
        assert clips_dir.exists()


class TestMergeVideos:
    """Tests for merge_videos function."""

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.concatenate_videoclips")
    @patch("backend.video_utils.time.time")
    def test_merge_videos_success(
        self,
        mock_time,
        mock_concatenate,
        mock_video_clip_class,
        mock_clips_dir,
        mock_base_dir
    ):
        """Test successful video merging."""
        mock_time.return_value = 9876543210

        # Create source video files
        video1 = mock_clips_dir / "video1.mp4"
        video2 = mock_clips_dir / "video2.mp4"
        video1.write_text("fake video 1")
        video2.write_text("fake video 2")

        # Setup mocks
        mock_clip1 = MagicMock()
        mock_clip2 = MagicMock()
        mock_final = MagicMock()

        mock_video_clip_class.side_effect = [mock_clip1, mock_clip2]
        mock_concatenate.return_value = mock_final

        # Call merge_videos
        result = merge_videos(["clips/video1.mp4", "clips/video2.mp4"])

        # Verify calls
        assert mock_video_clip_class.call_count == 2
        mock_concatenate.assert_called_once_with(
            [mock_clip1, mock_clip2], method="compose"
        )
        mock_final.write_videofile.assert_called_once()
        mock_final.close.assert_called_once()
        mock_clip1.close.assert_called_once()
        mock_clip2.close.assert_called_once()

        # Verify result
        assert "finalrender_9876543210.mp4" in result

    def test_merge_videos_file_not_found(self, mock_clips_dir, mock_base_dir):
        """Test merge_videos with missing video file."""
        with pytest.raises(FileNotFoundError, match="Video not found"):
            merge_videos(["clips/missing.mp4", "clips/also_missing.mp4"])

    @patch("backend.video_utils.VideoFileClip")
    def test_merge_videos_first_file_missing(
        self, mock_video_clip_class, mock_clips_dir, mock_base_dir
    ):
        """Test merge_videos when first file exists but second doesn't."""
        video1 = mock_clips_dir / "video1.mp4"
        video1.write_text("fake video 1")

        with pytest.raises(FileNotFoundError, match="Video not found.*video2.mp4"):
            merge_videos(["clips/video1.mp4", "clips/video2.mp4"])

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.concatenate_videoclips")
    @patch("backend.video_utils.time.time")
    def test_merge_videos_closes_clips_on_error(
        self,
        mock_time,
        mock_concatenate,
        mock_video_clip_class,
        mock_clips_dir,
        mock_base_dir
    ):
        """Test that merge_videos closes clips even when an error occurs."""
        mock_time.return_value = 1111111111

        # Create source files
        video1 = mock_clips_dir / "video1.mp4"
        video2 = mock_clips_dir / "video2.mp4"
        video1.write_text("fake video 1")
        video2.write_text("fake video 2")

        # Setup mocks
        mock_clip1 = MagicMock()
        mock_clip2 = MagicMock()
        mock_video_clip_class.side_effect = [mock_clip1, mock_clip2]

        # Make concatenate raise an error
        mock_concatenate.side_effect = Exception("Concatenation failed")

        # Call merge_videos and expect exception
        with pytest.raises(Exception, match="Concatenation failed"):
            merge_videos(["clips/video1.mp4", "clips/video2.mp4"])

        # Verify clips were still closed
        mock_clip1.close.assert_called_once()
        mock_clip2.close.assert_called_once()

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.concatenate_videoclips")
    @patch("backend.video_utils.time.time")
    def test_merge_videos_empty_list(
        self,
        mock_time,
        mock_concatenate,
        mock_video_clip_class,
        mock_clips_dir,
        mock_base_dir
    ):
        """Test merge_videos with empty list of videos."""
        mock_time.return_value = 1234567890
        mock_final = MagicMock()
        mock_concatenate.return_value = mock_final

        # Call with empty list
        result = merge_videos([])

        # Should call concatenate with empty list
        mock_concatenate.assert_called_once_with([], method="compose")
        assert "finalrender_1234567890.mp4" in result

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.concatenate_videoclips")
    @patch("backend.video_utils.time.time")
    def test_merge_videos_creates_clips_dir(
        self,
        mock_time,
        mock_concatenate,
        mock_video_clip_class,
        tmp_path,
        monkeypatch
    ):
        """Test that merge_videos creates clips directory if it doesn't exist."""
        mock_time.return_value = 1234567890

        # Setup directories
        clips_dir = tmp_path / "clips"
        monkeypatch.setattr("backend.video_utils.CLIPS_DIR", clips_dir)
        monkeypatch.setattr("backend.video_utils.BASE_DIR", tmp_path)

        # Create source in a different location
        video1 = tmp_path / "video1.mp4"
        video1.write_text("fake video")

        # Setup mocks
        mock_clip = MagicMock()
        mock_final = MagicMock()
        mock_video_clip_class.return_value = mock_clip
        mock_concatenate.return_value = mock_final

        assert not clips_dir.exists()

        # Call merge_videos with absolute path
        merge_videos([str(video1)])

        # Verify clips directory was created
        assert clips_dir.exists()


# ============================================================================
# INTEGRATION-STYLE TESTS
# ============================================================================


class TestIntegration:
    """Integration-style tests that test multiple components together."""

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.time.time")
    def test_upload_and_trim_workflow(
        self, mock_time, mock_video_clip_class, client, mock_clips_dir
    ):
        """Test complete workflow: upload then trim."""
        mock_time.return_value = 1234567890

        # Step 1: Upload video
        upload_data = {
            "videofile": (io.BytesIO(b"fake video data"), "original.mp4")
        }

        upload_response = client.post(
            "/upload_video",
            data=upload_data,
            content_type="multipart/form-data"
        )

        assert upload_response.status_code == 200
        uploaded_path = upload_response.get_data(as_text=True)
        assert "clips/original.mp4" in uploaded_path

        # Step 2: Mock VideoFileClip for trimming
        mock_clip = MagicMock()
        mock_trimmed = MagicMock()
        mock_clip.subclip.return_value = mock_trimmed
        mock_video_clip_class.return_value = mock_clip

        # Step 3: Trim the uploaded video
        trim_payload = {
            "videofile": "clips/original.mp4",
            "trim_start": 2,
            "trim_end": 8
        }

        trim_response = client.post(
            "/edit_video/trim",
            data=json.dumps(trim_payload),
            content_type="application/json"
        )

        assert trim_response.status_code == 200
        trim_data = trim_response.get_json()
        assert trim_data["status"] == "success"
        assert "edited_" in trim_data["edited_videopath"]

    @patch("backend.video_utils.VideoFileClip")
    @patch("backend.video_utils.concatenate_videoclips")
    @patch("backend.video_utils.time.time")
    def test_upload_multiple_and_merge_workflow(
        self,
        mock_time,
        mock_concatenate,
        mock_video_clip_class,
        client,
        mock_clips_dir
    ):
        """Test complete workflow: upload multiple videos then merge."""
        mock_time.return_value = 9999999999

        # Upload first video
        data1 = {
            "videofile": (io.BytesIO(b"video 1 data"), "video1.mp4")
        }
        response1 = client.post(
            "/upload_video",
            data=data1,
            content_type="multipart/form-data"
        )
        assert response1.status_code == 200

        # Upload second video
        data2 = {
            "videofile": (io.BytesIO(b"video 2 data"), "video2.mp4")
        }
        response2 = client.post(
            "/upload_video",
            data=data2,
            content_type="multipart/form-data"
        )
        assert response2.status_code == 200

        # Mock video clips for merging
        mock_clip1 = MagicMock()
        mock_clip2 = MagicMock()
        mock_final = MagicMock()
        mock_video_clip_class.side_effect = [mock_clip1, mock_clip2]
        mock_concatenate.return_value = mock_final

        # Merge the videos
        merge_payload = {
            "videoscount": 2,
            "video0": "clips/video1.mp4",
            "video1": "clips/video2.mp4"
        }

        merge_response = client.post(
            "/merged_render",
            data=json.dumps(merge_payload),
            content_type="application/json"
        )

        assert merge_response.status_code == 200
        merge_data = merge_response.get_json()
        assert merge_data["status"] == "success"
        assert "finalrender_" in merge_data["finalrender_videopath"]

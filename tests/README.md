# Video Editor Backend Tests

This directory contains comprehensive pytest tests for the video editor backend.

## Test Coverage

The test suite (`test_backend.py`) includes:

### API Route Tests
- **Health Check** - Tests the `/` endpoint
- **Clips Endpoint** - Tests serving video clips via `/clips/<filename>`
- **Upload Endpoint** - Tests video upload via `/upload_video`
- **Edit Endpoint** - Tests video editing (trim) via `/edit_video/trim`
- **Merge Endpoint** - Tests video merging via `/merged_render`

### Unit Tests
- **video_utils Functions**:
  - `ensure_clips_dir()` - Directory creation
  - `_resolve_clip_path()` - Path resolution
  - `_relative_clip_path()` - Path conversion
  - `trim_video()` - Video trimming with MoviePy mocking
  - `merge_videos()` - Video merging with MoviePy mocking

### Error Handling Tests
- Invalid inputs (negative times, wrong types, etc.)
- Missing files
- Missing parameters
- Generic exceptions

### Integration Tests
- Complete workflows: upload → trim
- Complete workflows: upload multiple → merge

## Running Tests

### Install Dependencies

First, install the test dependencies:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=backend --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Classes or Functions

```bash
# Run all tests in a specific class
pytest tests/test_backend.py::TestHealthEndpoint

# Run a specific test
pytest tests/test_backend.py::TestTrimVideo::test_trim_video_success
```

## Test Architecture

### Fixtures
- `app` - Flask application instance
- `client` - Flask test client for making HTTP requests
- `mock_clips_dir` - Temporary directory for test files
- `mock_base_dir` - Mock base directory
- `mock_video_clip` - Mock MoviePy VideoFileClip object

### Mocking Strategy
All MoviePy video processing is mocked to avoid:
- Requiring actual video files
- Long test execution times
- FFmpeg dependencies during testing

The tests verify:
- Correct function calls to MoviePy
- Proper error handling
- File path management
- API response formats

## Notes

- Tests use temporary directories via `pytest`'s `tmp_path` fixture
- No actual video processing occurs during tests
- All MoviePy imports are mocked with `unittest.mock`
- Tests are isolated and can run in any order

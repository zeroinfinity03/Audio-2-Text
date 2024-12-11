# Audio to Text Converter

A FastAPI web application that converts various audio formats to text using whisper.cpp, providing efficient CPU-based transcription.

## Supported Audio Formats

The application supports the following audio formats:
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- OGG (.ogg)
- WMA (.wma)
- AAC (.aac)
- FLAC (.flac)

All formats are automatically converted to WAV format (16kHz, mono) using FFmpeg before transcription.

## System Requirements

- Python 3.8 or higher
- C++ compiler
- FFmpeg (for audio conversion)
- CMake (for building whisper.cpp)

## Prerequisites Installation

Follow these steps in exact order:

### For macOS:
```bash
# 1. Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install required build tools and dependencies
brew install cmake
brew install ffmpeg
xcode-select --install  # Install Xcode Command Line Tools

# 3. Verify installations
cmake --version
ffmpeg -version
```

### For Ubuntu/Debian:
```bash
# Install required tools
sudo apt-get update
sudo apt-get install -y cmake
sudo apt-get install -y ffmpeg
sudo apt-get install -y build-essential
```

### For Windows:
1. Install [CMake](https://cmake.org/download/)
2. Install [FFmpeg](https://ffmpeg.org/download.html)
3. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## Project Setup

1. Create and navigate to project directory:
```bash
mkdir audio-to-text
cd audio-to-text
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
.\venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install fastapi>=0.68.0 uvicorn>=0.15.0 python-multipart>=0.0.5 jinja2>=3.0.1 aiofiles>=0.7.0 python-dotenv>=0.19.0 requests>=2.31.0 tqdm>=4.66.1
```

4. Clone and build whisper.cpp:
```bash
# Clone whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git

# Build whisper.cpp
cd whisper.cpp
make
cd ..

# Download the model
cd whisper.cpp
bash ./models/download-ggml-model.sh base.en
cd ..
```

5. Verify the setup:
```bash
# Check if executable exists
ls whisper.cpp/build/bin/main

# Check if model exists
ls whisper.cpp/models/ggml-base.en.bin

# Verify FFmpeg installation
ffmpeg -version
```

## Project Structure

Your directory should look like this:
```
audio-to-text/
├── app.py              # FastAPI application
├── requirements.txt    # Python dependencies
├── templates/         # HTML templates
│   └── index.html    # Web interface
└── whisper.cpp/      # Whisper.cpp directory
    ├── build/        # Build directory
    │   └── bin/      
    │       └── main  # Compiled whisper.cpp binary
    └── models/       # Model directory
        └── ggml-base.en.bin  # Downloaded model
```

## Running the Application

1. Make sure you're in the project root directory with virtual environment activated

2. Start the server:
```bash
uvicorn app:app --reload
```

3. Open your browser and go to:
```
http://localhost:8000
```

## Troubleshooting Common Issues

### 1. Audio Format Issues
If you encounter problems with audio files:
```bash
# Check if FFmpeg can read your file
ffmpeg -i your_audio_file

# Test manual conversion
ffmpeg -i your_audio_file -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

### 2. Executable Not Found
If you get "whisper.cpp executable not found":
```bash
# Check the executable path
ls -l whisper.cpp/build/bin/main

# If not found, rebuild whisper.cpp
cd whisper.cpp
make clean
make
cd ..
```

### 3. FFmpeg Issues
If you get MP3 conversion errors:
```bash
# Verify FFmpeg installation
ffmpeg -version

# Reinstall if needed
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

### 4. Build Issues
If whisper.cpp build fails:
```bash
# Make sure cmake is installed
cmake --version

# Clean and rebuild
cd whisper.cpp
make clean
make
cd ..
```

## Usage

1. Access the web interface at http://localhost:8000
2. Upload any supported audio file using the drag-and-drop interface
3. Click "Transcribe Audio"
4. Wait for the transcription to complete
5. View the transcribed text
6. Use the copy button to copy the text to clipboard

## Technical Details

- **Framework**: FastAPI
- **ML Model**: whisper.cpp (C++ implementation of Whisper)
- **Audio Processing**: FFmpeg for audio format conversion
- **Frontend**: Modern HTML/CSS with dark mode support
- **Features**: 
  - Multi-format audio support
  - Drag-and-drop file upload
  - Progress indication
  - Copy to clipboard functionality
  - Dark mode support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for the efficient C++ implementation
- FastAPI team for the excellent web framework

## System Verification

Check your system configuration:
```bash
curl http://localhost:8000/system-info
```

Expected output:
```json
{
    "os": "Your OS",
    "python_version": "3.8+",
    "whisper_cpp_path": "/path/to/whisper.cpp/build/bin/main",
    "model_path": "/path/to/whisper.cpp/models/ggml-base.en.bin",
    "arm_mac": true/false
}
```



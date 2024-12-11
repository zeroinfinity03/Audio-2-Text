import os
import sys
import subprocess
from fastapi import FastAPI, UploadFile, Request, HTTPException, status, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
from pathlib import Path
import tempfile
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="MP3 to Text Converter")

# Initialize templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get the absolute path to the project directory
BASE_DIR = "/Users/suryavikramsingh/Desktop/mp3 to text"

# Path to whisper.cpp executable and model
WHISPER_CPP_PATH = os.path.join(BASE_DIR, "whisper.cpp", "build", "bin", "main")
MODEL_PATH = os.path.join(BASE_DIR, "whisper.cpp", "models", "ggml-base.en.bin")

# Add debug logging
logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Whisper.cpp path: {WHISPER_CPP_PATH}")
logger.info(f"Model path: {MODEL_PATH}")

def check_whisper_cpp():
    """Check if whisper.cpp is properly built"""
    if not os.path.exists(WHISPER_CPP_PATH):
        raise FileNotFoundError(
            "whisper.cpp executable not found. Please build whisper.cpp first."
        )
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model not found. Please download the model first using the provided script."
        )

def initialize_model():
    """Initialize the Whisper.cpp model"""
    try:
        check_whisper_cpp()
        logger.info("Whisper.cpp and model verified successfully")
        return True
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise

# Initialize model
logger.info("Starting initialization...")
WHISPER_INITIALIZED = initialize_model()

def convert_to_wav(input_path):
    """Convert any audio format to WAV using ffmpeg"""
    output_path = os.path.splitext(input_path)[0] + '.wav'
    try:
        # Add more detailed ffmpeg options for better conversion
        subprocess.run([
            'ffmpeg',
            '-i', input_path,        # Input file
            '-ar', '16000',          # Sample rate: 16kHz
            '-ac', '1',              # Channels: mono
            '-c:a', 'pcm_s16le',     # Codec: 16-bit PCM
            '-y',                    # Overwrite output file
            output_path
        ], check=True, capture_output=True, text=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr}")
        raise Exception(f"Audio conversion failed: {e.stderr}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "transcription": None,
            "error": None
        }
    )

@app.post("/", response_class=HTMLResponse)
async def transcribe(request: Request, audio_file: UploadFile = File(...)):
    """Handle audio transcription"""
    # Check file extension
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.wma', '.aac', '.flac'}
    file_ext = os.path.splitext(audio_file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}",
                "transcription": None
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    logger.info(f"Received {file_ext} file: {audio_file.filename}")
    
    if not WHISPER_INITIALIZED:
        logger.error("Whisper not initialized")
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Whisper.cpp initialization failed", "transcription": None},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    mp3_path = None
    wav_path = None
    try:
        # Save uploaded MP3 file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            content = await audio_file.read()
            tmp.write(content)
            mp3_path = tmp.name
            logger.info(f"Saved MP3 file to: {mp3_path}")

        # Convert to WAV
        wav_path = convert_to_wav(mp3_path)
        logger.info(f"Converted to WAV: {wav_path}")

        # Use whisper.cpp for transcription
        command = [
            WHISPER_CPP_PATH,
            "-m", MODEL_PATH,
            "-f", wav_path,
            "-l", "en"
        ]
        
        logger.info(f"Running command: {' '.join(command)}")
        
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Get transcription from output
        transcription = process.stdout.strip()
        if not transcription:
            logger.error("No transcription in stdout")
            logger.error(f"Process stdout: {process.stdout}")
            logger.error(f"Process stderr: {process.stderr}")
            raise Exception("No transcription output found")
        
        logger.info(f"Transcription: {transcription}")

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "transcription": transcription, "error": None}
        )

    finally:
        # Cleanup temporary files
        if mp3_path and os.path.exists(mp3_path):
            os.unlink(mp3_path)
        if wav_path and os.path.exists(wav_path):
            os.unlink(wav_path)

@app.get("/system-info")
async def system_info():
    """Get system information"""
    return {
        "os": platform.platform(),
        "python_version": platform.python_version(),
        "whisper_cpp_path": WHISPER_CPP_PATH,
        "model_path": MODEL_PATH,
        "arm_mac": platform.machine() == "arm64"
    }

@app.post("/test-upload")
async def test_upload(audio_file: UploadFile = File(...)):
    """Test endpoint for file uploads"""
    return {
        "filename": audio_file.filename,
        "content_type": audio_file.content_type,
        "size": len(await audio_file.read())
    }


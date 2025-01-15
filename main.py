from fastapi import FastAPI, HTTPException, Request
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from pydantic import BaseModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class YouTubeURL(BaseModel):
    url: str

@app.post("/get_transcript")
async def get_transcript(request: Request, youtube_url: YouTubeURL):
    # Log the request method and body
    logger.info(f"Request method: {request.method}")
    body = await request.json()
    logger.info(f"Request body: {body}")
    
    try:
        logger.info(f"Processing URL: {youtube_url.url}")
        video_id = youtube_url.url.split('watch?v=')[1].split('&')[0]
        logger.info(f"Video ID: {video_id}")
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = None
            
            # Log available transcripts
            available = transcript_list.manual_generated_transcripts
            logger.info(f"Available transcripts: {available}")
            
            try:
                transcript = transcript_list.find_transcript(['es'])
                language = "español"
            except NoTranscriptFound:
                try:
                    transcript = transcript_list.find_transcript(['en'])
                    language = "inglés"
                except NoTranscriptFound:
                    transcript = transcript_list.find_transcript()
                    language = transcript.language
            
            if transcript:
                transcript_data = transcript.fetch()
                transcripcion = ' '.join(segment['text'] for segment in transcript_data)
                return {
                    "transcription": transcripcion,
                    "language": language,
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Error getting transcript: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "video_id": video_id
            }
            
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/")
async def root():
    return {"message": "YouTube Transcript API Service"}

# Add a test endpoint
@app.get("/test")
async def test():
    return {"status": "Service is running"}
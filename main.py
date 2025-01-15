from fastapi import FastAPI, HTTPException
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
async def get_transcript(youtube_url: YouTubeURL):
    logger.info(f"Recibida petición para URL: {youtube_url.url}")
    try:
        video_id = youtube_url.url.split('watch?v=')[1].split('&')[0]
        logger.info(f"Video ID extraído: {video_id}")
        
        try:
            logger.info("Intentando obtener transcripciones...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Intentar obtener transcripción en este orden: español, inglés, cualquiera
            transcript = None
            
            try:
                logger.info("Intentando obtener transcripción en español...")
                transcript = transcript_list.find_transcript(['es'])
                language = "español"
            except NoTranscriptFound:
                try:
                    logger.info("Intentando obtener transcripción en inglés...")
                    transcript = transcript_list.find_transcript(['en'])
                    language = "inglés"
                except NoTranscriptFound:
                    logger.info("Intentando obtener cualquier transcripción disponible...")
                    transcript = transcript_list.find_transcript()
                    language = transcript.language
            
            if transcript:
                logger.info(f"Transcripción encontrada en {language}")
                transcript_data = transcript.fetch()
                transcripcion = ' '.join(segment['text'] for segment in transcript_data)
                logger.info("Transcripción recuperada exitosamente")
                return {
                    "transcription": transcripcion,
                    "language": language,
                    "success": True
                }
                
        except TranscriptsDisabled as e:
            logger.error(f"Transcripciones deshabilitadas: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "Los subtítulos están deshabilitados para este video",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Error obteniendo transcripción: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error obteniendo transcripción",
                    "details": str(e)
                }
            )
            
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Error procesando la petición",
                "details": str(e)
            }
        )
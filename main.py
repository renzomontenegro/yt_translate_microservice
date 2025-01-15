from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic import BaseModel

app = FastAPI()

class YouTubeURL(BaseModel):
    url: str

@app.post("/get_transcript")
async def get_transcript(youtube_url: YouTubeURL):
    try:
        video_id = youtube_url.url.split('watch?v=')[1].split('&')[0]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Intentar obtener transcripción en español, luego en inglés, luego cualquiera
        try:
            transcript = transcript_list.find_transcript(['es'])
        except:
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                transcript = transcript_list.find_transcript()
        
        transcript_data = transcript.fetch()
        transcripcion = ' '.join(segment['text'] for segment in transcript_data)
        
        return {"transcription": transcripcion}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Añadir un endpoint de prueba
@app.get("/")
async def root():
    return {"message": "YouTube Transcript API Service"}
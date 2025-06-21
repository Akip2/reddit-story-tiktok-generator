import edge_tts
import os
from datetime import datetime

async def create_audio(text: str) -> str:
    os.makedirs("speech", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"./speech/audio_{timestamp}.mp3"
    
    communicate = edge_tts.Communicate(
        text, voice="en-US-BrianNeural"
    )
    await communicate.save(filename)
    
    return filename
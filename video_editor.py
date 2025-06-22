import ffmpeg, os, random, whisper
from datetime import datetime
from mutagen.mp3 import MP3
from whisper.utils import get_writer

GAMEPLAY_DIR = "./gameplay"

model = whisper.load_model("base")

def get_random_gameplay():
    return os.path.join(GAMEPLAY_DIR, random.choice(os.listdir(GAMEPLAY_DIR)))

def get_audio_duration(audio_path: str) -> float:
    audio = MP3(audio_path)
    return audio.info.length

def get_video_duration(video_path: str) -> float:
    probe = ffmpeg.probe(video_path)
    return float(probe["format"]["duration"])

def generate_srt_file(audio_path: str) -> str:
    transcription = model.transcribe(audio_path, fp16=False, language="en")
    
    filename = "subtitles.srt"
    sub_writer = get_writer("srt", "./output")
    sub_writer(transcription, filename)
    
    return "./output/"+filename

def add_subtitles_to_video(video_path: str, sub_path: str):
    temp_path = video_path + ".temp.mp4"

    ffmpeg.input(video_path).output(
        temp_path,
        vf=f"subtitles={sub_path}",
        vcodec='libx264',
        acodec='copy'
    ).run()

    os.replace(temp_path, video_path)
    
def add_gameplay_to_audio(audio_path: str) -> str:
    video_path = get_random_gameplay()
    audio_duration = get_audio_duration(audio_path)
    video_duration = get_video_duration(video_path)

    max_start = max(0, video_duration - audio_duration)
    start_time = random.uniform(0, max_start)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"output/video_{timestamp}.mp4"
    os.makedirs("output", exist_ok=True)
    
    input_video = ffmpeg.input(video_path, ss=start_time, t=audio_duration)
    input_audio = ffmpeg.input(audio_path)

    video_stream = input_video['v:0']
    audio_stream = input_audio['a:0']
    
    # Output combined video+audio to mp4 file
    (
        ffmpeg
        .output(video_stream, audio_stream, filename, vcodec='libx264', acodec='aac')
        .run()
    )
    
    return filename

def generate_video_from_audio(audio_path: str):
    video_path = add_gameplay_to_audio(audio_path)
    sub_path = generate_srt_file(audio_path)
    
    add_subtitles_to_video(video_path, sub_path)
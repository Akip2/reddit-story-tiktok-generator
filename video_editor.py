import ffmpeg, os, random, whisper
from mutagen.mp3 import MP3
from whisper.utils import get_writer
from utils import generate_filename

GAMEPLAY_DIR = "./gameplay"
SUBTITLES_DIR = "./output/subs"
TEMP_VIDEO_DIR = "./output/temp"
RESULT_DIR = "./output/result"

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
    os.makedirs(SUBTITLES_DIR, exist_ok=True)
    transcription = model.transcribe(audio_path, fp16=False, language="en")
    
    filename = generate_filename(SUBTITLES_DIR, "subtitles", "srt")
    filepath = SUBTITLES_DIR+"/"+filename
    sub_writer = get_writer("srt", SUBTITLES_DIR)
    sub_writer(transcription, filename)
    
    return filepath

def add_subtitles_to_video(video_path: str, sub_path: str):
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    filepath = RESULT_DIR+"/"+generate_filename(RESULT_DIR, "result", "mp4")

    ffmpeg.input(video_path).output(
        filepath,
        vf=f"subtitles={sub_path}",
        vcodec='libx264',
        acodec='copy'
    ).run()
    
def add_gameplay_to_audio(audio_path: str) -> str:
    os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

    video_path = get_random_gameplay()
    audio_duration = get_audio_duration(audio_path)
    video_duration = get_video_duration(video_path)

    max_start = max(0, video_duration - audio_duration)
    start_time = random.uniform(0, max_start)
    
    filename = generate_filename(TEMP_VIDEO_DIR, "video", "mp4")
    filepath = f"{TEMP_VIDEO_DIR}/{filename}"
    
    input_video = ffmpeg.input(video_path, ss=start_time, t=audio_duration)
    input_audio = ffmpeg.input(audio_path)

    video_stream = input_video['v:0']
    audio_stream = input_audio['a:0']
    
    # Output combined video+audio to mp4 file
    (
        ffmpeg
        .output(video_stream, audio_stream, filepath, vcodec='libx264', acodec='aac')
        .run()
    )
    
    return filepath

def generate_video_from_audio(audio_path: str):
    video_path = add_gameplay_to_audio(audio_path)
    sub_path = generate_srt_file(audio_path)
    
    add_subtitles_to_video(video_path, sub_path)
import ffmpeg, os, random, whisper
from mutagen.mp3 import MP3
from whisper.utils import get_writer
from utils import generate_filename
from datetime import timedelta
import srt

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

def split_transcription_to_srt(transcription, max_words=10):
    segments = []
    for seg in transcription["segments"]:
        words = seg["text"].strip().split()
        start = seg["start"]
        end = seg["end"]
        duration = end - start

        if len(words) <= max_words:
            segments.append(srt.Subtitle(
                index=len(segments)+1,
                start=timedelta(seconds=start),
                end=timedelta(seconds=end),
                content=" ".join(words)
            ))
        else:
            for i in range(0, len(words), max_words):
                chunk = words[i:i+max_words]
                chunk_start = start + (i / len(words)) * duration
                chunk_end = start + ((i + len(chunk)) / len(words)) * duration
                segments.append(srt.Subtitle(
                    index=len(segments)+1,
                    start=timedelta(seconds=chunk_start),
                    end=timedelta(seconds=chunk_end),
                    content=" ".join(chunk)
                ))
    return segments

def generate_srt_file(audio_path: str) -> str:
    os.makedirs(SUBTITLES_DIR, exist_ok=True)
    transcription = model.transcribe(audio_path, fp16=False, language="en")
    
    subtitles = split_transcription_to_srt(transcription, max_words=10)
    
    filename = generate_filename(SUBTITLES_DIR, "subtitles", "srt")
    filepath = SUBTITLES_DIR + "/" + filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))
    
    return filepath

def add_subtitles_to_video(video_path: str, sub_path: str):
    os.makedirs(RESULT_DIR, exist_ok=True)

    is_ass = sub_path.endswith(".ass")
    filepath = RESULT_DIR + "/" + generate_filename(RESULT_DIR, "result", "mp4")
    
    subtitle_filter = f"ass={sub_path}" if is_ass else f"subtitles={sub_path}"

    ffmpeg.input(video_path).output(
        filepath,
        vf=subtitle_filter,
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
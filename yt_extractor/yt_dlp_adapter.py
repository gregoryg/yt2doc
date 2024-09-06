import typing

import yt_dlp

from dataclasses import dataclass
from pathlib import Path


@dataclass
class YtChapter:
    title: str
    start_time: float
    end_time: float


@dataclass
class YtVideoInfo:
    video_id: str
    title: str
    audio_path: Path
    chapters: typing.List[YtChapter]


class YtDlpAdapter:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def extract_video_info(self, video_url: str):
        ydl_opts = {
            "quiet": True,
            "outtmpl": f"{self.temp_dir}/%(id)s.%(ext)s",
            "format": "m4a/bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            response = ydl.extract_info(video_url, download=True)
            video_id = response["id"]
            title = response["title"]
            audio_path = self.temp_dir / f"{video_id}.m4a"
            chapter_objects = response["chapters"] if response["chapters"] else []
            chapters = [YtChapter(**chapter) for chapter in chapter_objects]

            return YtVideoInfo(
                video_id=video_id,
                title=title,
                audio_path=audio_path,
                chapters=chapters,
            )

import tempfile
import time
import typing

import typer

from pathlib import Path

from faster_whisper import WhisperModel

from yt_extractor.yt_dlp_adapter import YtDlpAdapter
from yt_extractor.whisper_adapter import WhisperAdapter


class Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.seconds = time.perf_counter() - self._start


app = typer.Typer()


@app.command()
def extract(
    video: typing.Optional[str] = typer.Option(
        None, "--video", help="URL of the video to extract"
    ),
    playlist: typing.Optional[str] = typer.Option(
        None, "--playlist", help="URL of the playlist to extract"
    ),
    by_chapter: typing.Annotated[
        bool,
        typer.Option(
            "--by-chapter", help="If should split the audio by YouTube video chapter"
        ),
    ] = False,
    whisper_model_size: typing.Optional[str] = typer.Option(
        None, "--whisper-model", help="Whisper model to use for transcription"
    ),
    whisper_compute_type: typing.Optional[str] = typer.Option(
        None,
        "--whisper-compute-type",
        help="Whisper compute type to use for transcription",
    ),
    whisper_device: typing.Optional[str] = typer.Option(
        None, "--whisper-device", help="Whisper device type to use for transcription"
    ),
):
    if not whisper_model_size:
        whisper_model_size = "base"

    if not whisper_compute_type:
        whisper_compute_type = "int8"

    if not whisper_device:
        whisper_device = "cpu"

    whisper_model = WhisperModel(
        model_size_or_path=whisper_model_size,
        device=whisper_device,
        compute_type=whisper_compute_type,
    )
    whisper_adapter = WhisperAdapter(model=whisper_model)

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        yt_dlp_adapter = YtDlpAdapter(temp_dir=temp_dir)

        if video:
            typer.echo(f"extracting video {video}", err=True)

            with Timer() as yt_dl_timer:
                video_info = yt_dlp_adapter.extract_video_info(video_url=video)
            typer.echo(
                f"Video downloading time: {yt_dl_timer.seconds} seconds", err=True
            )

            with Timer() as transcribe_timer:
                if by_chapter:
                    transcripts_by_chapter = whisper_adapter.transcribe_by_chapter(
                        audio_path=video_info.audio_path,
                        title=video_info.title,
                        chapters=video_info.chapters,
                    )
                    transcript = "\n\n".join(
                        [
                            f"## {chapter.title}\n\n{chapter.text}"
                            for chapter in transcripts_by_chapter
                        ]
                    )
                else:
                    transcript = whisper_adapter.transcribe_full_text(
                        audio_path=video_info.audio_path
                    )
            typer.echo(
                f"Transcription time: {transcribe_timer.seconds} seconds", err=True
            )
            typer.echo(f"# {video_info.title}\n\n{video}\n\n{transcript}")

        elif playlist:
            typer.echo(f"extracting playlist {playlist}", err=True)
        else:
            typer.echo("Please provide either --video or --playlist option", err=True)


@app.command()
def summarize(
    video: typing.Optional[str] = typer.Option(
        None, "--video", help="URL of the video to summarize"
    ),
    playlist: typing.Optional[str] = typer.Option(
        None, "--playlist", help="URL of the playlist to summarize"
    ),
):
    if video:
        typer.echo(f"summarizing video {video}", err=True)
    elif playlist:
        typer.echo(f"summarizing playlist {playlist}", err=True)
    else:
        typer.echo("Please provide either --video or --playlist option", err=True)


if __name__ == "__main__":
    app()

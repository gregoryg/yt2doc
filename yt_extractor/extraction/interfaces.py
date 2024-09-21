import typing

from pydantic import BaseModel


class TranscriptChapter(BaseModel):
    title: str
    text: str


class ChapteredTranscript(BaseModel):
    url: str
    title: str
    chapters: typing.Sequence[TranscriptChapter]


class ChapteredTranscribedPlaylist(BaseModel):
    url: str
    title: str
    transcripts: typing.Sequence[ChapteredTranscript]


MetaDict = typing.Dict[str, typing.Union[str, int, float]]


class IFileCache(typing.Protocol):
    def get_chaptered_transcript(
        self, video_id: str
    ) -> typing.Optional[typing.Sequence[TranscriptChapter]]: ...
    def cache_chaptered_transcript(
        self,
        video_id: str,
        chapters: typing.Sequence[TranscriptChapter],
    ) -> None: ...


class IExtractor(typing.Protocol):
    def extract_by_chapter(
        self,
        video_url: str,
        skip_cache: bool,
    ) -> ChapteredTranscript: ...

    def extract_playlist_by_chapter(
        self, playlist_url: str, skip_cache: bool
    ) -> ChapteredTranscribedPlaylist: ...

from datetime import datetime
from typing import Annotated, Literal, Protocol

from pydantic import StringConstraints

VideoID = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=11, max_length=11, pattern=r"[A-Za-z0-9_-]{11}"
    ),
]

UserGroup = Literal[0, 1, 2]


class VideoInfosP(Protocol):
    id: VideoID
    title: str
    date: datetime
    duration: str
    thumbnail_url: str


class ChannelInfosP(Protocol):
    id: str
    name: str
    uploads_playlist_id: str


class ProcessedTranscriptP(Protocol):
    tokens_count: int
    is_generated: bool
    text: str


class VideoP(Protocol):
    infos: VideoInfosP
    channel_infos: ChannelInfosP
    transcript: ProcessedTranscriptP | None


class UserSummaryP(Protocol):
    user_group: UserGroup
    summary: str


class SummaryP(Protocol):
    video_infos: VideoInfosP
    channel_infos: ChannelInfosP
    base: str
    short: str
    title: str
    user_groups: list

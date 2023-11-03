from datetime import datetime
from typing import Annotated, Literal, Protocol

from pydantic import StringConstraints

VideoID = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=11, max_length=11, pattern=r"[A-Za-z0-9_-]{11}"
    ),
]

ChannelID = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=24, max_length=24, pattern=r"[A-Za-z0-9_-]{24}"
    ),
]

UserGroup = Literal[0, 1, 2]


class VideoInfoP(Protocol):
    id: VideoID
    title: str
    date: datetime
    duration: str
    thumbnail_url: str


class ChannelInfoP(Protocol):
    id: ChannelID
    name: str
    uploads_playlist_id: str


class ProcessedTranscriptP(Protocol):
    tokens_count: int
    is_generated: bool
    text: str


class VideoP(Protocol):
    info: VideoInfoP
    channel_info: ChannelInfoP
    transcript: ProcessedTranscriptP | None


class SummaryP(Protocol):
    video_info: VideoInfoP
    channel_info: ChannelInfoP
    base: str
    topics: str


class UserStoryP(Protocol):
    user_group: UserGroup
    story: str


class StoryP(Protocol):
    video_info: VideoInfoP
    channel_info: ChannelInfoP
    short: str
    title: str
    user_stories: list[UserStoryP]


class NewsletterP(Protocol):
    group_id: UserGroup
    stories: list[StoryP]
    summary: str
    html: str

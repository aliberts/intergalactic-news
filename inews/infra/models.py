from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, RootModel, StringConstraints

VideoID = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=11, max_length=11, pattern=r"[A-Za-z0-9_-]{11}"
    ),
]


class RootModelList(RootModel):
    root: list[Any]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, item):
        self.root[key] = item

    def __len__(self):
        return len(self.root)

    def append(self, item):
        self.root.append(item)

    def pop(self, key):
        self.root.pop(key)


class Transcript(BaseModel):
    channel_id: str
    channel_name: str
    video_id: VideoID
    video_title: str
    date: datetime
    duration: str
    is_generated: bool
    tokens_count: int
    transcript: str


class TranscriptList(RootModelList):
    root: list[Transcript]


class Video(BaseModel):
    id: VideoID
    title: str
    date: datetime
    duration: str


class Channel(BaseModel):
    id: str
    name: str
    uploads_playlist_id: str
    last_week_videos: list[Video] = Field(default_factory=lambda: [])


class ChannelList(RootModelList):
    root: list[Channel]


class UserBase(BaseModel):
    science_cat: Literal[0, 1, 2]


class User(UserBase):
    name: str
    email: str
    science_cat: Literal[0, 1, 2]


class BaseSummary(BaseModel):
    tokens_count: int
    summary: str


class SummaryInfo(BaseModel):
    channel_id: str
    channel_name: str
    video_id: VideoID
    video_title: str
    date: datetime
    duration: str
    from_generated: bool


class UserSummary(BaseModel):
    user: UserBase
    summary: str


class UserSummaryList(RootModelList):
    root: list[UserSummary]


class Summary(BaseModel):
    infos: SummaryInfo
    base_summary: BaseSummary
    user_summaries: UserSummaryList = Field(default_factory=lambda: [])

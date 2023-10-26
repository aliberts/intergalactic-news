from datetime import datetime
from typing import Any, List, Literal

from pydantic import BaseModel, Field, RootModel

# TODO: Type VideoID with regex: ([A-Za-z0-9_\-]{11})


class RootModelList(RootModel):
    root: List[Any]

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
    video_id: str
    video_title: str
    channel_id: str
    channel_name: str
    date: datetime
    is_generated: bool
    tokens_count: int
    transcript: str


class TranscriptList(RootModelList):
    root: List[Transcript]


class Video(BaseModel):
    id: str
    title: str
    date: datetime


class VideoList(RootModelList):
    root: List[Video]


class Channel(BaseModel):
    id: str
    name: str
    uploads_playlist_id: str
    recent_videos: VideoList


class ChannelList(RootModelList):
    root: List[Channel]


class User(BaseModel):
    age_cat: Literal[0, 1, 2]
    science_cat: Literal[0, 1, 2]


class BaseSummary(BaseModel):
    tokens_count: int
    summary: str


class SummaryInfo(BaseModel):
    video_id: str
    video_title: str
    channel_id: str
    channel_name: str
    date: datetime
    from_generated: bool


class UserSummary(BaseModel):
    user: User
    summary: str


class UserSummaryList(RootModelList):
    root: List[UserSummary]


class Summary(BaseModel):
    infos: SummaryInfo
    base_summary: BaseSummary
    user_summaries: UserSummaryList = Field(default_factory=lambda: [])

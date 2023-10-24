from datetime import datetime
from typing import List

from pydantic import BaseModel, RootModel


class Transcript(BaseModel):
    video_id: str
    video_title: str
    channel_id: str
    channel_name: str
    date: datetime
    is_generated: bool
    tokens_count: int
    transcript: str


class TranscriptList(RootModel):
    root: List[Transcript]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, item):
        self.root[key] = item

    def __len__(self):
        return len(self.root)

    def pop(self, key):
        self.root.pop(key)


class Video(BaseModel):
    id: str
    title: str
    date: datetime


class VideoList(RootModel):
    root: List[Video]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, item):
        self.root[key] = item

    def __len__(self):
        return len(self.root)

    def pop(self, key):
        self.root.pop(key)


class Channel(BaseModel):
    id: str
    name: str
    uploads_playlist_id: str
    recent_videos: VideoList


class ChannelList(RootModel):
    root: List[Channel]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, item):
        self.root[key] = item

    def __len__(self):
        return len(self.root)

    def pop(self, key):
        self.root.pop(key)


class User(BaseModel):
    age: int
    science_level: str

    @property
    def age_bin(self):
        if self.age <= 10:
            return ("a 6 years-old child",)
        elif self.age > 10 and self.age <= 18:
            return ("a 14 years-old teenager",)
        elif self.age > 18:
            return ("an adult",)


class BaseSummary(BaseModel):
    video_id: str
    video_title: str
    channel_id: str
    channel_name: str
    date: datetime
    from_generated: bool
    tokens_count: int
    summary: str


class BaseSummaryList(RootModel):
    root: List[BaseSummary]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, item):
        self.root[key] = item

    def __len__(self):
        return len(self.root)

    def pop(self, key):
        self.root.pop(key)


class UserSummary(BaseModel):
    user: User
    summaries: BaseSummaryList

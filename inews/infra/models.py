from datetime import datetime
from typing import List

from pydantic import BaseModel


class YoutubeVideoTranscript(BaseModel):
    video_id: str
    video_title: str
    channel_id: str
    channel_name: str
    date: datetime
    is_generated: bool
    tokens_count: int
    transcript: str


class YoutubeVideoTranscriptList(BaseModel):
    transcripts: List[YoutubeVideoTranscript]


class YoutubeVideo(BaseModel):
    id: str
    title: str
    date: datetime


class YoutubeChannel(BaseModel):
    id: str
    name: str
    uploads_playlist_id: str
    recent_videos: List[YoutubeVideo]


class YoutubeChannelList(BaseModel):
    channels: List[YoutubeChannel]


class YoutubeVideoList(BaseModel):
    videos: List[YoutubeVideo]


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


class BaseSummaryList(BaseModel):
    summaries: List[BaseSummary]


class UserSummary(BaseModel):
    user: User
    summaries: List[BaseSummary]

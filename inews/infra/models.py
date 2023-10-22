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

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class YoutubeChannel(BaseModel):
    id: str
    name: str
    uploads_playlist_id: str
    last_video_id: str
    last_video_date: datetime
    last_video_title: str


class YoutubeChannelList(BaseModel):
    channels: List[YoutubeChannel]


class YoutubeVideo(BaseModel):
    id: str
    title: str
    date: datetime
    en_transcript: str
    transcript_type: Optional[str] = None


class YoutubeVideoList(BaseModel):
    videos: List[YoutubeVideo]

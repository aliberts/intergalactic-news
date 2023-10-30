import json
from datetime import datetime, timezone
from functools import cached_property
from typing import Any

import pendulum
from pydantic import BaseModel, Field, RootModel, computed_field
from unidecode import unidecode
from youtube_transcript_api._transcripts import Transcript as YtTranscript

from inews.domain import openai, preprocessing, youtube
from inews.infra import io
from inews.infra.types import UserGroup, VideoID

USER_GROUPS = [0, 1, 2]
MIN_VIDEO_DURATION = 2  # minimum video length in minutes


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

    def sort(self, *args, **kwargs):
        self.root.sort(*args, **kwargs)

    def append(self, item):
        self.root.append(item)

    def pop(self, key):
        self.root.pop(key)


class Video(BaseModel):
    id: VideoID
    title: str
    date: datetime
    duration: str
    thumbnail_url: str

    @classmethod
    def init_from_info(cls, video_info: dict):
        return cls(
            **{
                "id": video_info["id"],
                "title": unidecode(video_info["snippet"]["title"]),
                "date": video_info["snippet"]["publishedAt"],
                "duration": video_info["contentDetails"]["duration"],
                "thumbnail_url": video_info["snippet"]["thumbnails"]["medium"]["url"],
            }
        )

    @cached_property
    def is_not_short(self) -> bool:
        return pendulum.parse(self.duration).minutes >= MIN_VIDEO_DURATION

    @cached_property
    def available_transcript(self) -> YtTranscript | None:
        return youtube.get_available_transcript(self.id)

    @cached_property
    def is_from_this_week(self) -> bool:
        return (datetime.now(timezone.utc) - self.date).days < 7

    @cached_property
    def is_valid(self) -> bool:
        return (
            self.is_not_short and self.is_from_this_week and (self.available_transcript is not None)
        )


class VideoList(RootModelList):
    root: list[Video]

    @classmethod
    def init_from_ids(cls, videos_id: list[VideoID]):
        videos_info = youtube.get_videos_info(videos_id)
        videos = []
        for video_info in videos_info["items"]:
            videos.append(Video.init_from_info(video_info))

        return cls.model_validate(videos)

    def drop_invalids(self) -> None:
        self.root = [video for video in self.root if video.is_valid]


class Channel(BaseModel):
    id: str
    name: str
    uploads_playlist_id: str
    last_week_videos: VideoList = Field(default_factory=lambda: [])

    @classmethod
    def init_from_info(cls, channel_info: dict):
        return cls(
            **{
                "id": channel_info["id"],
                "uploads_playlist_id": channel_info["contentDetails"]["relatedPlaylists"][
                    "uploads"
                ],
                "name": channel_info["snippet"]["title"],
                "last_week_videos": [],
            }
        )

    def get_recent_videos_id(self) -> list[VideoID]:
        uploads_info = youtube.get_channel_recent_videos_id(self.uploads_playlist_id)
        videos_id = []
        for item in uploads_info["items"]:
            videos_id.append(item["snippet"]["resourceId"]["videoId"])

        return videos_id


class ChannelList(RootModelList):
    root: list[Channel]

    @classmethod
    def init_from_ids(cls, channels_id: list[str]):
        channels_info = youtube.get_channels_info(channels_id)
        channels = []
        for channel_info in channels_info["items"]:
            channels.append(Channel.init_from_info(channel_info))
        return cls.model_validate(channels)

    @classmethod
    def init_from_file(cls):
        with open(io.CHANNELS_LOCAL_FILE) as file:
            json_data = json.load(file)
        return cls.model_validate(json_data)

    def update_last_week_videos(self) -> None:
        for channel in self.root:
            videos_id = channel.get_recent_videos_id()
            videos = VideoList.init_from_ids(videos_id)
            videos.drop_invalids()
            channel.last_week_videos = videos

    def save(self) -> None:
        with open(io.CHANNELS_LOCAL_FILE, "w") as file:
            json.dump(self.model_dump(mode="json"), file, indent=4)


class Transcript(BaseModel):
    channel_id: str
    channel_name: str
    video_id: VideoID
    video_title: str
    date: datetime
    duration: str
    thumbnail_url: str
    is_generated: bool
    tokens_count: int
    transcript: str

    @classmethod
    def init_from_file(cls, video_id: VideoID):
        for file_path in io.TRANSCRIPTS_LOCAL_PATH.rglob(f"*.{video_id}.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            return cls.model_validate(json_data)

    @classmethod
    def init_from_channel_and_video(cls, channel: Channel, video: Video):
        if not io.is_new(video.id):
            return cls.init_from_file(video.id)

        raw_transcript = video.available_transcript.fetch()
        transcript = preprocessing.format_transcript(raw_transcript)
        tokens_count = preprocessing.count_tokens(transcript)
        return cls(
            **{
                "channel_id": channel.id,
                "channel_name": channel.name,
                "video_id": video.id,
                "video_title": video.title,
                "date": video.date,
                "duration": video.duration,
                "thumbnail_url": video.thumbnail_url,
                "is_generated": video.available_transcript.is_generated,
                "tokens_count": tokens_count,
                "transcript": transcript,
            }
        )

    def save(self) -> None:
        file_name = f"""{self.date.strftime("%Y-%m-%d")}.{self.video_id}.json"""
        file_path = io.TRANSCRIPTS_LOCAL_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(self.model_dump(mode="json"), file, indent=4)


class TranscriptList(RootModelList):
    root: list[Transcript]

    @classmethod
    def init_from_channels(cls, channels: ChannelList):
        transcripts = []
        for channel in channels:
            for video in channel.last_week_videos:
                if video.available_transcript is not None:
                    transcripts.append(Transcript.init_from_channel_and_video(channel, video))
        return cls.model_validate(transcripts)

    @classmethod
    def init_from_files(cls, channels: ChannelList):
        transcripts = []
        for channel in channels:
            for video in channel.last_week_videos:
                transcripts.append(Transcript.init_from_file(video.id))
        return cls.model_validate(transcripts)

    def save(self):
        for transcript in self.root:
            transcript.save()


class User(BaseModel):
    name: str
    email: str
    science_cat: UserGroup


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
    thumbnail_url: str
    is_generated: bool

    @classmethod
    def init_from_transcript(cls, transcript: Transcript):
        return cls(**transcript.model_dump(exclude={"tokens_count", "transcript"}))


class UserSummary(BaseModel):
    user_group: UserGroup
    summary: str


class UserSummaryList(RootModelList):
    root: list[UserSummary]


class Summary(BaseModel):
    infos: SummaryInfo
    base: str

    @classmethod
    def init_from_file(cls, video_id: VideoID):
        for file_path in io.SUMMARIES_LOCAL_PATH.rglob(f"*.{video_id}.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            return cls.model_validate(json_data)

    @classmethod
    def init_from_transcript(cls, transcript: Transcript):
        infos = SummaryInfo.init_from_transcript(transcript)
        base_summary = openai.get_base_summary(
            transcript.video_title, transcript.channel_name, transcript.transcript
        )
        return cls(infos=infos, base=base_summary)

    @computed_field
    @cached_property
    def short(self) -> str:
        return openai.get_short_summary(self.infos.video_title, self.infos.channel_name, self.base)

    @computed_field
    @cached_property
    def title(self) -> str:
        return openai.get_title(self.infos.video_title, self.infos.channel_name, self.base)

    @computed_field
    @cached_property
    def user_groups(self) -> UserSummaryList:
        user_summaries = []
        for group_id in USER_GROUPS:
            user_summary = openai.get_user_summary(
                self.infos.video_title, self.infos.channel_name, self.base, group_id
            )
            user_summaries.append(UserSummary(user_group=group_id, summary=user_summary))

        return UserSummaryList.model_validate(user_summaries)

    def save(self) -> None:
        file_name = f"""{self.infos.date.strftime("%Y-%m-%d")}.{self.infos.video_id}.json"""
        file_path = io.SUMMARIES_LOCAL_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(self.model_dump(mode="json"), file, indent=4)

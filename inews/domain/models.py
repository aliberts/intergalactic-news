import json
from datetime import datetime, timezone
from functools import cached_property
from typing import Any

import pendulum
from pydantic import BaseModel, Field, RootModel
from unidecode import unidecode
from youtube_transcript_api._transcripts import Transcript

from inews.domain import llm, preprocessing, youtube
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


class VideoInfos(BaseModel):
    id: VideoID
    title: str
    date: datetime
    duration: str
    thumbnail_url: str

    @classmethod
    def init_from_api_response(cls, api_response: dict):
        return cls(
            **{
                "id": api_response["id"],
                "title": unidecode(api_response["snippet"]["title"]),
                "date": api_response["snippet"]["publishedAt"],
                "duration": api_response["contentDetails"]["duration"],
                "thumbnail_url": api_response["snippet"]["thumbnails"]["medium"]["url"],
            }
        )

    @cached_property
    def is_not_short(self) -> bool:
        return pendulum.parse(self.duration).minutes >= MIN_VIDEO_DURATION

    @cached_property
    def is_from_this_week(self) -> bool:
        return (datetime.now(timezone.utc) - self.date).days < 7

    @property
    def is_valid(self) -> bool:
        return self.is_not_short and self.is_from_this_week


class VideoInfosList(RootModelList):
    root: list[VideoInfos] = Field(default_factory=list)

    @classmethod
    def init_from_ids(cls, videos_id: list[VideoID]):
        api_response = youtube.get_videos_infos(videos_id)
        videos = []
        for item in api_response["items"]:
            videos.append(VideoInfos.init_from_api_response(item))

        return cls.model_validate(videos)

    def drop_invalids(self) -> None:
        self.root = [video for video in self.root if video.is_valid]


class ChannelInfos(BaseModel):
    id: str
    name: str
    uploads_playlist_id: str

    @classmethod
    def init_from_api_response(cls, api_response: dict):
        return cls(
            **{
                "id": api_response["id"],
                "name": api_response["snippet"]["title"],
                "uploads_playlist_id": api_response["contentDetails"]["relatedPlaylists"][
                    "uploads"
                ],
            }
        )


class Channel(BaseModel):
    infos: ChannelInfos
    last_week_videos: VideoInfosList = Field(default_factory=lambda: VideoInfosList())

    @classmethod
    def init_from_api_response(cls, api_response: dict):
        infos = ChannelInfos.init_from_api_response(api_response)
        return cls(infos=infos)

    def get_recent_videos_id_from_api(self) -> list[VideoID]:
        uploads_info = youtube.get_channel_recent_videos_id(self.infos.uploads_playlist_id)
        videos_id = []
        for item in uploads_info["items"]:
            videos_id.append(item["snippet"]["resourceId"]["videoId"])

        return videos_id

    def update_last_week_videos(self) -> None:
        videos_id = self.get_recent_videos_id_from_api()
        videos = VideoInfosList.init_from_ids(videos_id)
        videos.drop_invalids()
        self.last_week_videos = videos


class ChannelList(RootModelList):
    root: list[Channel] = Field(default_factory=list)

    @classmethod
    def init_from_api_with_ids(cls, channels_id: list[str]):
        api_response = youtube.get_channels_info(channels_id)
        channels = []
        for item in api_response["items"]:
            channels.append(Channel.init_from_api_response(item))
        return cls.model_validate(channels)

    @classmethod
    def init_from_file(cls):
        with open(io.CHANNELS_LOCAL_FILE) as file:
            json_data = json.load(file)
        return cls.model_validate(json_data)

    def update_last_week_videos(self) -> None:
        for channel in self.root:
            channel.update_last_week_videos()

    def save(self) -> None:
        with open(io.CHANNELS_LOCAL_FILE, "w") as file:
            json.dump(self.model_dump(mode="json"), file, indent=4)


class ProcessedTranscript(BaseModel):
    tokens_count: int
    is_generated: bool
    text: str

    @classmethod
    def init_from_transcript(cls, transcript: Transcript):
        raw_transcript = transcript.fetch()
        text = preprocessing.format_transcript(raw_transcript)
        tokens_count = preprocessing.count_tokens(text)
        return cls(tokens_count=tokens_count, is_generated=transcript.is_generated, text=text)


class Video(BaseModel):
    infos: VideoInfos
    channel_infos: ChannelInfos
    transcript: ProcessedTranscript | None = None

    @classmethod
    def init_from_file(cls, video_id: VideoID):
        for file_path in io.TRANSCRIPTS_LOCAL_PATH.rglob(f"*.{video_id}.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            return cls.model_validate(json_data)

    def get_available_transcript(self) -> None:
        available_transcript = youtube.get_available_transcript(self.infos.id)
        if available_transcript is None:
            self.transcript = None
        else:
            self.transcript = ProcessedTranscript.init_from_transcript(available_transcript)

    def save(self) -> None:
        file_name = f"""{self.infos.date.strftime("%Y-%m-%d")}.{self.infos.id}.json"""
        file_path = io.TRANSCRIPTS_LOCAL_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(self.model_dump(mode="json"), file, indent=4)


class VideoList(RootModelList):
    root: list[Video] = Field(default_factory=list)

    @classmethod
    def init_from_channels(cls, channels: ChannelList):
        videos = []
        for channel in channels:
            for video_infos in channel.last_week_videos:
                videos.append(Video(infos=video_infos, channel_infos=channel.infos))
        return cls.model_validate(videos)

    @classmethod
    def init_from_all_files(cls):
        videos = []
        for file_path in io.TRANSCRIPTS_LOCAL_PATH.rglob("*.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            videos.append(Video.model_validate(json_data))
        return cls.model_validate(videos)

    @classmethod
    def init_from_files_with_videos_id(cls, videos_id: list[VideoID]):
        videos = []
        for video_id in videos_id:
            videos.append(Video.init_from_file(video_id))
        return cls.model_validate(videos)

    def get_available_transcripts(self) -> None:
        for video in self.root:
            video.get_available_transcript()

    def drop_no_transcripts(self) -> None:
        self.root = [video for video in self.root if video.transcript is not None]

    def save(self) -> None:
        for video in self.root:
            video.save()


class User(BaseModel):
    name: str
    email: str
    science_cat: UserGroup


class UserSummary(BaseModel):
    user_group: UserGroup
    summary: str = ""


class UserSummaryList(RootModelList):
    root: list[UserSummary] = Field(default_factory=list)


class Summary(BaseModel):
    video_infos: VideoInfos
    channel_infos: ChannelInfos
    base: str = ""
    short: str = ""
    title: str = ""
    user_groups: UserSummaryList = Field(default_factory=lambda: UserSummaryList())

    @classmethod
    def init_from_file(cls, video_id: VideoID):
        for file_path in io.SUMMARIES_LOCAL_PATH.rglob(f"*.{video_id}.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            return cls.model_validate(json_data)

    @classmethod
    def init_from_video(cls, video: Video):
        return cls(video_infos=video.infos, channel_infos=video.channel_infos)

    def get_base_from_transcript(self, transcript: str) -> None:
        self.base = llm.get_base_summary(
            self.video_infos.title, self.channel_infos.name, transcript
        )

    def get_short(self) -> None:
        self.short = llm.get_short_summary(
            self.video_infos.title, self.channel_infos.name, self.base
        )

    def get_title(self) -> None:
        self.title = llm.get_title_summary(
            self.video_infos.title, self.channel_infos.name, self.base
        )

    def get_user_groups(self) -> None:
        user_summaries = []
        for group_id in USER_GROUPS:
            user_summary = llm.get_user_summary(
                self.video_infos.title, self.channel_infos.name, self.base, group_id
            )
            user_summaries.append(UserSummary(user_group=group_id, summary=user_summary))

        self.user_groups = UserSummaryList.model_validate(user_summaries)

    def get_all(self, transcript: str) -> None:
        self.get_base_from_transcript(transcript)
        self.get_short()
        self.get_title()
        self.get_user_groups()

    def save(self) -> None:
        file_name = f"""{self.video_infos.date.strftime("%Y-%m-%d")}.{self.video_infos.id}.json"""
        file_path = io.SUMMARIES_LOCAL_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(self.model_dump(mode="json"), file, indent=4)


class SummaryList(RootModelList):
    root: list[Summary] = Field(default_factory=list)

    @classmethod
    def init_from_videos(cls, videos: VideoList):
        summaries = []
        for video in videos:
            summaries.append(Summary.init_from_video(video))
        return cls.model_validate(summaries)

    @classmethod
    def init_from_files_with_videos(cls, videos: VideoList):
        summaries = []
        for video in videos:
            summaries.append(Summary.init_from_file(video.infos.id))
        return cls.model_validate(summaries)

    @classmethod
    def init_from_files_with_videos_id(cls, videos_id: list[VideoID]):
        summaries = []
        for video_id in videos_id:
            summaries.append(Summary.init_from_file(video_id))
        return cls.model_validate(summaries)

    def get_bases_from_videos(self, videos: VideoList) -> None:
        mapping = {video.infos.id: idx for idx, video in enumerate(videos)}
        for summary in self.root:
            idx = mapping[summary.video_infos.id]
            summary.get_base_from_transcript(videos[idx].transcript.text)

    def get_shorts(self) -> None:
        for summary in self.root:
            summary.get_short()

    def get_titles(self) -> None:
        for summary in self.root:
            summary.get_title()

    def get_user_groups(self) -> None:
        for summary in self.root:
            summary.get_user_groups()

    def get_all(self, videos: VideoList) -> None:
        self.get_bases_from_videos(videos)
        self.get_shorts()
        self.get_titles()
        self.get_user_groups()

    def save(self) -> None:
        for summary in self.root:
            summary.save()


class Newsletter(BaseModel):
    user_group: UserGroup
    html: str

    @classmethod
    def init_from_summaries(cls, user_group: UserGroup, summaries: SummaryList):
        ...

import json
from datetime import datetime, timezone
from functools import cached_property
from typing import Any

import pendulum
from pydantic import BaseModel, Field, RootModel
from tqdm import tqdm
from unidecode import unidecode
from youtube_transcript_api._transcripts import Transcript

from inews.domain import llm, mailing, preprocessing, youtube
from inews.infra import io
from inews.infra.types import UserGroup, VideoID

data_config = io.get_data_config()


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
        return pendulum.parse(self.duration).minutes >= data_config["min_video_duration"]

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
    recent_videos: VideoInfosList = Field(default_factory=VideoInfosList)

    @classmethod
    def init_from_api_response(cls, api_response: dict):
        infos = ChannelInfos.init_from_api_response(api_response)
        return cls(infos=infos)

    def get_recent_videos_id_from_api(self) -> list[VideoID]:
        api_response = youtube.get_channel_recent_videos_id(self.infos.uploads_playlist_id)
        videos_id = []
        for item in api_response["items"]:
            videos_id.append(item["snippet"]["resourceId"]["videoId"])
        return videos_id

    def update_recent_videos(self) -> None:
        videos_id = self.get_recent_videos_id_from_api()
        videos = VideoInfosList.init_from_ids(videos_id)
        videos.drop_invalids()
        self.recent_videos = videos


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

    def update_recent_videos(self) -> None:
        print("Updating channels recent videos")
        for channel in tqdm(self.root):
            channel.update_recent_videos()

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
    allow_requests: bool = True
    transcript: ProcessedTranscript | None = None

    @classmethod
    def init_from_file(cls, video_id: VideoID):
        for file_path in io.TRANSCRIPTS_LOCAL_PATH.rglob(f"*.{video_id}.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            video = cls.model_validate(json_data)
            video.allow_requests = False
            return video

    def get_available_transcript(self) -> None:
        if not self.allow_requests:
            return

        available_transcript = youtube.get_available_transcript(self.infos.id)
        if available_transcript is None:
            self.transcript = None
        else:
            self.transcript = ProcessedTranscript.init_from_transcript(available_transcript)

    def save(self) -> None:
        file_name = f"""{self.infos.date.date()}.{self.infos.id}.json"""
        file_path = io.TRANSCRIPTS_LOCAL_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(self.model_dump(mode="json", exclude={"allow_requests"}), file, indent=4)


class VideoList(RootModelList):
    root: list[Video] = Field(default_factory=list)

    @classmethod
    def init_from_channels(cls, channels: ChannelList, use_local_files: bool = True):
        videos = []
        for channel in channels:
            for video_infos in channel.recent_videos:
                if io.video_in_local_files(video_infos.id) and use_local_files:
                    videos.append(Video.init_from_file(video_infos.id))
                else:
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

    def allow_request(self, allow: bool):
        for video in self.root:
            video.allow_requests = allow

    @classmethod
    def init_from_files_with_videos_id(cls, videos_id: list[VideoID]):
        videos = []
        for video_id in videos_id:
            videos.append(Video.init_from_file(video_id))
        return cls.model_validate(videos)

    def get_available_transcripts(self) -> None:
        print("Getting transcripts")
        for video in tqdm(self.root):
            video.get_available_transcript()

    def drop_no_transcripts(self) -> None:
        self.root = [video for video in self.root if video.transcript is not None]

    def save(self) -> None:
        for video in self.root:
            video.save()


class Summary(BaseModel):
    video_infos: VideoInfos
    channel_infos: ChannelInfos
    allow_requests: bool = True
    topics: str = ""
    base: str = ""

    @classmethod
    def init_from_file(cls, video_id: VideoID):
        for file_path in io.SUMMARIES_LOCAL_PATH.rglob(f"*.{video_id}.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            summary = cls.model_validate(json_data)
            summary.allow_requests = False
            return summary

    @classmethod
    def init_from_video(cls, video: Video):
        return cls(video_infos=video.infos, channel_infos=video.channel_infos)

    def get_base_from_video(self, video: Video) -> None:
        if self.allow_requests:
            self.base = llm.get_base_summary(self, video)

    def get_topics(self) -> None:
        if self.allow_requests:
            self.topics = llm.get_topics(self)

    def save(self) -> None:
        file_name = f"""{self.video_infos.date.date()}.{self.video_infos.id}.json"""
        file_path = io.SUMMARIES_LOCAL_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(self.model_dump(mode="json", exclude={"allow_requests"}), file, indent=4)


class SummaryList(RootModelList):
    root: list[Summary] = Field(default_factory=list)

    @classmethod
    def init_from_videos(cls, videos: VideoList, use_local_files: bool = True):
        summaries = []
        for video in videos:
            if io.summary_in_local_files(video.infos.id) and use_local_files:
                summaries.append(Summary.init_from_file(video.infos.id))
            else:
                summaries.append(Summary.init_from_video(video))
        return cls.model_validate(summaries)

    @classmethod
    def init_from_files_with_videos_id(cls, videos_id: list[VideoID]):
        summaries = []
        for video_id in videos_id:
            summaries.append(Summary.init_from_file(video_id))
        return cls.model_validate(summaries)

    def allow_request(self, allow: bool):
        for summary in self.root:
            summary.allow_requests = allow

    def get_bases_from_videos(self, videos: VideoList) -> None:
        mapping = {video.infos.id: idx for idx, video in enumerate(videos)}
        print("Getting base summaries")
        for summary in tqdm(self.root):
            idx = mapping[summary.video_infos.id]
            summary.get_base_from_video(videos[idx])

    def get_topics(self) -> None:
        print("Getting topics")
        for summary in tqdm(self.root):
            summary.get_topics()

    def drop_irrelevants(self) -> None:
        print("Selecting stories")
        selection = llm.get_stories_selection_from_topics(self)
        try:
            self.root = [
                summary
                for (summary, include) in zip(self.root, selection, strict=True)
                if include == "yes"
            ]
        except ValueError:
            Warning("Stories could not be selected, every story will be included.")

    def save(self) -> None:
        for summary in self.root:
            summary.save()


class User(BaseModel):
    name: str
    email: str
    science_cat: UserGroup


class UserStory(BaseModel):
    user_group: UserGroup
    user_story: str = ""


class UserStoryList(RootModelList):
    root: list[UserStory] = Field(default_factory=list)


class Story(BaseModel):
    video_infos: VideoInfos
    channel_infos: ChannelInfos
    allow_requests: bool = True
    short: str = ""
    title: str = ""
    user_stories: UserStoryList = Field(default_factory=UserStoryList)

    @classmethod
    def init_from_file(cls, video_id: VideoID):
        for file_path in io.STORIES_LOCAL_PATH.rglob(f"*.{video_id}.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            summary = cls.model_validate(json_data)
            summary.allow_requests = False
            return summary

    @classmethod
    def init_from_summary(cls, summary: Summary):
        return cls(video_infos=summary.video_infos, channel_infos=summary.channel_infos)

    def get_short_from_summary(self, summary: Summary) -> None:
        if self.allow_requests:
            self.short = llm.get_short_summary(summary)

    def get_title_from_summary(self, summary: Summary) -> None:
        if self.allow_requests:
            self.title = llm.get_title_summary(summary)

    def get_user_groups_from_summary(self, summary: Summary) -> None:
        if not self.allow_requests:
            return

        user_summaries = []
        for group_id in data_config["user_groups"]:
            user_summary = llm.get_user_story(summary, group_id)
            user_summaries.append(UserStory(user_group=group_id, user_story=user_summary))
        self.user_stories = UserStoryList.model_validate(user_summaries)
        self.save()

    def save(self) -> None:
        file_name = f"""{self.video_infos.date.date()}.{self.video_infos.id}.json"""
        file_path = io.STORIES_LOCAL_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(self.model_dump(mode="json", exclude={"allow_requests"}), file, indent=4)


class StoryList(RootModelList):
    root: list[Story] = Field(default_factory=list)

    @classmethod
    def init_from_summaries(cls, summaries: SummaryList, use_local_files: bool = True):
        stories = []
        for summary in summaries:
            if io.story_in_local_files(summary.video_infos.id) and use_local_files:
                stories.append(Story.init_from_file(summary.video_infos.id))
            else:
                stories.append(Story.init_from_summary(summary))
        return cls.model_validate(stories)

    @classmethod
    def init_from_all_files(cls):
        stories = []
        for file_path in io.STORIES_LOCAL_PATH.rglob("*.json"):
            with open(file_path) as file:
                json_data = json.load(file)
            stories.append(Story.model_validate(json_data))
        stories = cls.model_validate(stories)
        stories.allow_requests(False)
        return stories

    def allow_requests(self, allow: bool):
        for story in self.root:
            story.allow_requests = allow

    def get_shorts_from_summaries(self, summaries: SummaryList) -> None:
        print("Getting short stories")
        mapping = {summary.video_infos.id: idx for idx, summary in enumerate(summaries)}
        for story in tqdm(self.root):
            idx = mapping[story.video_infos.id]
            story.get_short_from_summary(summaries[idx])

    def get_titles_from_summaries(self, summaries: SummaryList) -> None:
        print("Getting title stories")
        mapping = {summary.video_infos.id: idx for idx, summary in enumerate(summaries)}
        for story in tqdm(self.root):
            idx = mapping[story.video_infos.id]
            story.get_title_from_summary(summaries[idx])

    def get_user_groups_from_summaries(self, summaries: SummaryList) -> None:
        print("Getting user stories")
        mapping = {summary.video_infos.id: idx for idx, summary in enumerate(summaries)}
        for story in tqdm(self.root):
            idx = mapping[story.video_infos.id]
            story.get_user_groups_from_summary(summaries[idx])

    def save(self) -> None:
        for summary in self.root:
            summary.save()


class Newsletter(BaseModel):
    group_id: UserGroup
    stories: StoryList
    allow_requests: bool = True
    summary: str = ""
    html: str = ""

    @classmethod
    def init_from_summaries(cls, group_id: UserGroup, stories: StoryList):
        return cls(group_id=group_id, stories=stories)

    def make_html(self) -> None:
        self.html = mailing.create_newsletter(self.group_id, self.stories)

    def get_summary(self) -> None:
        if self.allow_requests:
            self.summary = llm.get_newsletter_summary(self.stories)

    def save(self) -> None:
        io.write_html(self.html, f"newsletter_testing_{self.group_id}")

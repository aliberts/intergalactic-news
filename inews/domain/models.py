from functools import cached_property
from pathlib import Path

import pendulum
import readtime
from pydantic import BaseModel, Field, computed_field
from youtube_transcript_api._transcripts import Transcript

from inews.domain import html, llm, mailing, preprocessing, youtube
from inews.infra import io
from inews.infra.types import (
    ChannelID,
    PendulumDateTime,
    RunEvent,
    UserGroup,
    VideoID,
    pprint_repr,
)

data_config = io.get_data_config()
mailing_config = io.get_mailing_config()


BaseModel.__repr__ = pprint_repr


class VideoInfo(BaseModel):
    id: VideoID
    channel_id: ChannelID
    title: str
    date: PendulumDateTime
    duration: str
    thumbnail_url: str
    use: bool = True

    @cached_property
    def is_not_short(self) -> bool:
        return pendulum.parse(self.duration).minutes >= data_config["min_video_duration"]

    @property
    def is_recent(self) -> bool:
        return (pendulum.now() - self.date).days < data_config["recent_videos_days_old"]

    @property
    def is_valid(self) -> bool:
        return self.is_not_short and self.is_recent


class ChannelInfo(BaseModel):
    id: ChannelID
    name: str
    uploads_playlist_id: str


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
    info: VideoInfo
    channel_info: ChannelInfo
    transcript: ProcessedTranscript | None = None
    allow_requests: bool = True

    @classmethod
    def init_from_file(cls, video_info: VideoInfo):
        file_path = io.TRANSCRIPTS_LOCAL_PATH / io.get_file_name(video_info)
        json_data = io.load_from_json_file(file_path)
        video = cls.model_validate(json_data)
        video.allow_requests = False
        return video

    def get_available_transcript(self) -> None:
        if not self.allow_requests:
            return

        available_transcript = youtube.get_available_transcript(self.info.id)
        if available_transcript is not None:
            self.transcript = ProcessedTranscript.init_from_transcript(available_transcript)

    @cached_property
    def valid_transcript(self) -> bool:
        if self.transcript is None:
            return False
        else:
            return (
                self.transcript.tokens_count >= data_config["tokens_min"]
                and self.transcript.tokens_count <= data_config["tokens_max"]
            )

    def save(self) -> None:
        file_path = io.TRANSCRIPTS_LOCAL_PATH / io.get_file_name(self.info)
        io.save_to_json_file(self.model_dump(mode="json", exclude={"allow_requests"}), file_path)


class Summary(BaseModel):
    video_info: VideoInfo
    channel_info: ChannelInfo
    topics: str = ""
    base: str = ""
    allow_requests: bool = True

    @classmethod
    def init_from_file(cls, video_info: VideoInfo):
        file_path = io.SUMMARIES_LOCAL_PATH / io.get_file_name(video_info)
        json_data = io.load_from_json_file(file_path)
        summary = cls.model_validate(json_data)
        summary.allow_requests = False
        return summary

    @classmethod
    def init_from_video(cls, video: Video):
        return cls(video_infos=video.info, channel_infos=video.channel_info)

    def get_base_from_video(self, video: Video, run: RunEvent) -> None:
        if self.allow_requests:
            self.base = llm.get_base_summary(self, video, run)

    def get_topics(self, run: RunEvent) -> None:
        if self.allow_requests:
            self.topics = llm.get_topics(self, run)

    def save(self) -> None:
        file_path = io.SUMMARIES_LOCAL_PATH / io.get_file_name(self.video_info)
        io.save_to_json_file(self.model_dump(mode="json", exclude={"allow_requests"}), file_path)


class User(BaseModel):
    name: str
    email: str
    science_cat: UserGroup


class UserStory(BaseModel):
    user_group: UserGroup
    user_story: str = ""


class Story(BaseModel):
    video_info: VideoInfo
    channel_info: ChannelInfo
    short: str = ""
    title: str = ""
    user_stories: list[UserStory] = Field(default_factory=list)
    allow_requests: bool = True

    @classmethod
    def init_from_file(cls, video_info: VideoInfo):
        file_path = io.STORIES_LOCAL_PATH / io.get_file_name(video_info)
        json_data = io.load_from_json_file(file_path)
        story = cls.model_validate(json_data)
        story.allow_requests = False
        return story

    @classmethod
    def init_from_summary(cls, summary: Summary):
        return cls(video_infos=summary.video_info, channel_infos=summary.channel_info)

    def get_short_from_summary(self, summary: Summary, run: RunEvent) -> None:
        if self.allow_requests:
            self.short = llm.get_short_summary(summary, run)

    def get_title_from_summary(self, summary: Summary, run: RunEvent) -> None:
        if self.allow_requests:
            self.title = llm.get_title_summary(summary, run)

    def get_user_groups_from_summary(self, summary: Summary, run: RunEvent) -> None:
        if not self.allow_requests:
            return

        user_stories = []
        for group_id, _ in enumerate(mailing_config["mc_group_interest_values"]):
            user_summary = llm.get_user_story(summary, group_id, run)
            user_stories.append(UserStory(user_group=group_id, user_story=user_summary))
        self.user_stories = user_stories
        self.save()

    def is_too_old(self) -> bool:
        max_days_old = data_config["newsletter_stories_days_old"]
        story_date = self.video_info.date
        return (pendulum.today() - story_date).days >= max_days_old

    def save(self) -> None:
        file_path = io.STORIES_LOCAL_PATH / io.get_file_name(self.video_info)
        io.save_to_json_file(self.model_dump(mode="json", exclude={"allow_requests"}), file_path)


class NewsletterInfo(BaseModel):
    date: PendulumDateTime

    @computed_field
    @cached_property
    def issue_number(self) -> int:
        first_issue_date = pendulum.parse(
            mailing_config["first_issue_date"], tz=mailing_config["timezone"]
        )
        return (self.date - first_issue_date).in_weeks() + 1

    @computed_field
    @cached_property
    def name(self) -> str:
        return f"Intergalactic News #{self.issue_number} - {self.date.date()}"

    @computed_field
    @cached_property
    def file_name(self) -> Path:
        return Path(f"issue_{self.issue_number:04}.json")

    @computed_field
    @cached_property
    def read_times(self) -> list[int]:
        read_times = []
        for group_idx, _ in enumerate(mailing_config["mc_group_interest_values"]):
            user_group_read_time = 0
            for story in self.stories:
                text_to_read = story.title + story.short + story.user_stories[group_idx].user_story
                user_group_read_time += readtime.of_text(text_to_read).seconds

            read_times.append(user_group_read_time)

        return read_times

    summary: str = ""
    stories: list[Story]

    def save(self) -> None:
        file_path = io.NEWSLETTERS_LOCAL_PATH / self.file_name
        io.save_to_json_file(self.model_dump(mode="json", exclude={"name", "file_name"}), file_path)


class Newsletter(BaseModel):
    info: NewsletterInfo
    group_id: UserGroup
    read_time: int
    html: str = ""

    @computed_field
    @cached_property
    def file_name(self) -> Path:
        return Path(f"issue_{self.info.issue_number:04}_{self.group_id}.html")

    def build_html(self) -> None:
        self.html = html.create_newsletter(self)

    def save_html_build(self) -> None:
        file_path = io.HTML_BUILD_PATH / self.file_name
        io.save_to_html_file(self.html, file_path)


class MCCampaign(BaseModel):
    html: str

    group_id: UserGroup
    issue_number: int
    date: PendulumDateTime

    mc_id: str = ""
    mc_list_id: str
    mc_group_interest_id: str
    mc_group_id: str

    test_emails: list[str]
    mail_preview: str
    reply_to: str
    from_name: str

    @computed_field
    @cached_property
    def title(self) -> str:
        return f"inews_{self.issue_number:04}_{self.group_id}"

    @computed_field
    @cached_property
    def mail_subject(self) -> str:
        return f"Intergalactic News #{self.issue_number} - {self.date.date()}"

    @computed_field
    @cached_property
    def settings(self) -> dict:
        return {
            "type": "regular",
            "recipients": {
                "segment_opts": {
                    "match": "all",
                    "conditions": [
                        {
                            "condition_type": "Interests",
                            "field": f"interests-{self.mc_group_interest_id}",
                            "op": "interestcontains",
                            "value": [self.mc_group_id],
                        }
                    ],
                },
                "list_id": self.mc_list_id,
            },
            "settings": {
                "title": self.title,
                "subject_line": self.mail_subject,
                "from_name": self.from_name,
                "reply_to": self.reply_to,
                "preview_text": self.mail_preview,
            },
            "content_type": "multichannel",
        }

    @classmethod
    def init_from_newsletter(cls, newsletter: Newsletter):
        config = io.get_mailing_config()
        config["group_id"] = newsletter.group_id
        config["issue_number"] = newsletter.info.issue_number
        config["date"] = newsletter.info.date
        config["html"] = newsletter.html
        config["mc_group_id"] = config["mc_group_interest_values"][newsletter.group_id]
        config["mail_preview"] = newsletter.info.summary
        return cls(**config)

    def create(self) -> None:
        self.mc_id = mailing.create_campaign(self)

    def set_html(self) -> None:
        mailing.set_campaign_html(self.mc_id, self.html)

    def send(self) -> None:
        mailing.send_campaign(self.mc_id)

    def send_test(self) -> None:
        mailing.send_campaign_test(self.mc_id, self.test_emails)

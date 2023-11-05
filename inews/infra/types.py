from pprint import pformat
from typing import Annotated, Any, Callable, Literal, Protocol

import pendulum
from pydantic import GetJsonSchemaHandler, RootModel, StringConstraints
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


def pprint_repr(base_model):
    return pformat(base_model.model_dump(mode="json"))


RootModel.__repr__ = pprint_repr


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


class _DateTimePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        from_datetime_schema = core_schema.chain_schema(
            [
                core_schema.datetime_schema(),
                core_schema.no_info_plain_validator_function(pendulum.instance),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_datetime_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(pendulum.DateTime),
                    from_datetime_schema,
                ]
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.datetime_schema())


PendulumDateTime = Annotated[pendulum.DateTime, _DateTimePydanticAnnotation]

VideoID = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=11, max_length=11, pattern=r"[A-Za-z0-9_-]{11}"
    ),
]

ChannelID = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=24, max_length=24, pattern=r"[A-Za-z0-9_-]{24}"
    ),
]

UserGroup = Literal[0, 1, 2]


class VideoInfoP(Protocol):
    id: VideoID
    title: str
    date: pendulum.DateTime
    duration: str
    thumbnail_url: str


class ChannelInfoP(Protocol):
    id: ChannelID
    name: str
    uploads_playlist_id: str


class ProcessedTranscriptP(Protocol):
    tokens_count: int
    is_generated: bool
    text: str


class VideoP(Protocol):
    info: VideoInfoP
    channel_info: ChannelInfoP
    transcript: ProcessedTranscriptP | None


class SummaryP(Protocol):
    video_info: VideoInfoP
    channel_info: ChannelInfoP
    base: str
    topics: str


class UserStoryP(Protocol):
    user_group: UserGroup
    story: str


class StoryP(Protocol):
    video_info: VideoInfoP
    channel_info: ChannelInfoP
    short: str
    title: str
    user_stories: list[UserStoryP]


class NewsletterInfoP(Protocol):
    issue_number: int
    date: pendulum.DateTime
    name: str
    file_name: str
    summary: str
    stories: list[StoryP]


class NewsletterP(Protocol):
    info: NewsletterInfoP
    group_id: UserGroup
    html: str


class MCCampaignP(Protocol):
    group_id: UserGroup
    issue_number: int
    date: pendulum.DateTime
    html: str
    mc_list_id: str
    mc_group_interest_id: str
    mc_group_id: str
    mail_preview: str
    reply_to: str
    from_name: str
    title: str
    mail_subject: str
    settings: dict

from inews.domain import mailing
from inews.domain.models import (
    USER_GROUPS,
    ChannelList,
    Newsletter,
    Summary,
    SummaryList,
    VideoList,
)
from inews.infra import io


def build_channels(from_file: bool = True) -> ChannelList:
    if from_file:
        channels = ChannelList.init_from_file()
    else:
        channels_id = io.get_channels_id()
        channels = ChannelList.init_from_api_with_ids(channels_id)

    return channels


def build_videos(channels: ChannelList, from_file: bool = True) -> VideoList:
    if from_file:
        videos = VideoList.init_from_all_files()
    else:
        videos = VideoList.init_from_channels(channels)

    return videos


def build_summaries(videos: VideoList, from_file: bool = True) -> SummaryList:
    if from_file:
        summaries = SummaryList.init_from_files_with_videos(videos)
    else:
        summaries = SummaryList.init_from_videos(videos)

    return summaries


def select_stories(summaries: SummaryList) -> SummaryList:
    ...
    # llm.get_stories_selection()


def build_newsletters(summaries: list[Summary]) -> list[Newsletter]:
    for group_id in USER_GROUPS:
        mailing.create_newsletter(group_id, summaries)

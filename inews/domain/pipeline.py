from datetime import datetime, timezone

import pendulum

from inews.domain import openai, youtube
from inews.infra import io
from inews.infra.models import BaseSummary, ChannelList, Summary, TranscriptList, UserBase, Video

MIN_VIDEO_DURATION = 2  # minimum video length in minutes


def build_channels() -> ChannelList:
    channels_id = io.get_channels_id()
    channels = youtube.get_channels_info(channels_id)
    io.write_channels_state(channels)
    return channels


def is_not_short(video: Video) -> bool:
    return pendulum.parse(video.duration).minutes >= MIN_VIDEO_DURATION


def transcript_available(video: Video) -> bool:
    return youtube.get_available_transcript(video.id) is not None


def is_less_than_a_week_old(video: Video) -> bool:
    return (datetime.now(timezone.utc) - video.date).days < 7


def keep_valid_videos(videos: list[Video]) -> list[Video]:
    filtered_videos = []
    for video in videos:
        if is_not_short(video) and transcript_available(video) and is_less_than_a_week_old(video):
            filtered_videos.append(video)
    return filtered_videos


def build_transcripts(channels: ChannelList) -> TranscriptList:
    for channel in channels:
        videos_id = youtube.get_channel_recent_videos_id(channel)
        videos = youtube.get_videos_info(videos_id)
        channel.last_week_videos = keep_valid_videos(videos)
    io.write_channels_state(channels)

    transcripts = youtube.get_transcripts(channels)
    io.write_transcripts(transcripts)
    return transcripts


def build_summaries(transcripts_list: TranscriptList) -> dict[str:BaseSummary]:
    users = [UserBase(science_cat=0), UserBase(science_cat=2)]
    for transcript in transcripts_list:
        summary_info = openai.get_summary_info(transcript)
        base_summary = openai.get_base_summary(transcript)
        summary = Summary(
            infos=summary_info,
            base_summary=base_summary,
            user_summaries=[],
        )
        io.write_summary(summary)  # checkpoint to save base summaries first
        for user in users:
            user_summary = openai.get_user_summary(summary, user)
            summary.user_summaries.append(user_summary)
        io.write_summary(summary)

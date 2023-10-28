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


def filter_short_videos(videos: list[Video]) -> list[Video]:
    filtered_videos = []
    for video in videos:
        if pendulum.parse(video.duration).minutes >= MIN_VIDEO_DURATION:
            filtered_videos.append(video)
    return filtered_videos


def filter_transcript_unavailable(videos: list[Video]) -> list[Video]:
    filtered_videos = []
    for video in videos:
        available_transcript = youtube.get_available_transcript(video.id)
        if available_transcript is not None:
            filtered_videos.append(video)
    return filtered_videos


def build_transcripts(channels: ChannelList) -> TranscriptList:
    for channel in channels:
        videos_id = youtube.get_channel_recent_videos_id(channel)
        videos = youtube.get_videos_info(videos_id)
        videos = filter_short_videos(videos)
        videos = filter_transcript_unavailable(videos)
        channel.recent_videos = videos[:3]
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

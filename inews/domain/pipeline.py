from inews.domain import mailing
from inews.infra import io
from inews.infra.models import USER_GROUPS, ChannelList, Newsletter, Summary, TranscriptList


def build_channels(initialize: bool = True) -> ChannelList:
    if initialize:
        channels_id = io.get_channels_id()
        channels = ChannelList.init_from_ids(channels_id)
        channels.save()
    else:
        channels = ChannelList.init_from_file()

    channels.update_last_week_videos()
    channels.save()
    return channels


def build_transcripts(channels: ChannelList, initialize: bool = True) -> TranscriptList:
    if initialize:
        transcripts = TranscriptList.init_from_channels(channels)
        transcripts.save()
    else:
        transcripts = TranscriptList.init_from_files(channels)

    return transcripts


def build_summaries(transcripts: TranscriptList, initialize: bool = True) -> list[Summary]:
    summaries = []
    for transcript in transcripts:
        if initialize:
            summary = Summary.init_from_transcript(transcript)
            summary.save()
            summaries.append(summary)
        else:
            summary = Summary.init_from_file(transcript.video_id)
            summaries.append(summary)

    return summaries


def build_newsletters(summaries: list[Summary]) -> list[Newsletter]:
    for group_id in USER_GROUPS:
        mailing.create_newsletter(group_id, summaries)

from inews.infra import io
from inews.infra.models import ChannelList, Summary, TranscriptList


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


def build_summaries(transcripts: TranscriptList) -> list[Summary]:
    summaries = []
    for transcript in transcripts:
        summary = Summary.init_from_transcript(transcript)
        summary.save()
        summaries.append(summary)

    return summaries

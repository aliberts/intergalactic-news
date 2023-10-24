import json
from pathlib import Path

import yaml

from inews.infra.models import (
    BaseSummary,
    BaseSummaryList,
    ChannelList,
    Transcript,
    TranscriptList,
    UserSummary,
)

CHANNELS_ID_FILE = Path("config/channels_id.yaml")
CHANNELS_STATE_FILE = Path("data/channels_state.json")
TRANSCRIPTS_DATA_PATH = Path("data/transcripts/")
BASE_SUMMARIES_DATA_PATH = Path("data/base_summaries/")
USER_SUMMARIES_DATA_PATH = Path("data/user_summaries/")


def get_channels_id() -> list:
    with open(CHANNELS_ID_FILE) as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def write_channels_state(channels_list) -> None:
    with open(CHANNELS_STATE_FILE, "w") as file:
        json.dump(channels_list.model_dump(mode="json"), file, indent=4)


def write_transcript(transcript: Transcript) -> None:
    file_name = f"{transcript.video_id}.json"
    file_path = TRANSCRIPTS_DATA_PATH / file_name
    with open(file_path, "w") as file:
        json.dump(transcript.model_dump(mode="json"), file, indent=4)


def write_transcripts(transcripts_list: TranscriptList) -> None:
    for transcript in transcripts_list:
        write_transcript(transcript)


def read_transcript(video_id: str) -> Transcript:
    transcript_file_path = TRANSCRIPTS_DATA_PATH / f"{video_id}.json"
    with open(transcript_file_path) as file:
        json_data = json.load(file)
    return Transcript.model_validate(json_data)


def read_transcripts() -> TranscriptList:
    transcripts_list = []
    for transcript_file_path in TRANSCRIPTS_DATA_PATH.rglob("*.json"):
        transcripts_list.append(read_transcript(transcript_file_path.stem))
    return TranscriptList.model_validate(transcripts_list)


def read_transcripts_from_channel_list(channels_list: ChannelList) -> TranscriptList:
    transcripts_list = []
    for channel in channels_list:
        for video in channel.recent_videos:
            transcripts_list.append(read_transcript(video.id))
    return TranscriptList.model_validate(transcripts_list)


def read_channels_state() -> ChannelList:
    with open(CHANNELS_STATE_FILE) as file:
        json_data = json.load(file)
    channels_list = ChannelList.model_validate(json_data)
    return channels_list


def is_new(video_id: str) -> bool:
    existing_videos_id = [file.stem for file in TRANSCRIPTS_DATA_PATH.rglob("*.json")]
    return video_id not in existing_videos_id


def read_summary(video_id: str, step: str) -> BaseSummary:
    if step == "base":
        summary_path = BASE_SUMMARIES_DATA_PATH
    elif step == "user":
        summary_path = USER_SUMMARIES_DATA_PATH
    else:
        raise ValueError

    transcript_file_path = summary_path / f"{video_id}.json"
    with open(transcript_file_path) as file:
        json_data = json.load(file)
    return BaseSummary.model_validate(json_data)


def write_base_summaries(summary_list: BaseSummaryList) -> None:
    for summary in summary_list:
        file_name = f"{summary.video_id}.json"
        file_path = BASE_SUMMARIES_DATA_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(summary.model_dump(mode="json"), file, indent=4)


def write_user_summaries(user_summary: UserSummary) -> None:
    for summary in user_summary.summaries:
        file_name = f"{summary.video_id}.json"
        file_path = USER_SUMMARIES_DATA_PATH / file_name
        with open(file_path, "w") as file:
            json.dump(
                (user_summary.user.model_dump(mode="json"), summary.model_dump(mode="json")),
                file,
                indent=4,
            )

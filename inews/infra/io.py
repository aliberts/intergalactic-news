import json
from pathlib import Path

import yaml

from inews.infra.models import (
    YoutubeChannelList,
    YoutubeVideoTranscript,
    YoutubeVideoTranscriptList,
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


def write_channels_state(channels_obj_list) -> None:
    with open(CHANNELS_STATE_FILE, "w") as file:
        json.dump(channels_obj_list.model_dump(mode="json"), file, indent=4)


def write_transcript(transcript_obj: YoutubeVideoTranscript) -> None:
    file_name = f"{transcript_obj.video_id}.json"
    file_path = TRANSCRIPTS_DATA_PATH / file_name
    with open(file_path, "w") as file:
        json.dump(transcript_obj.model_dump(mode="json"), file, indent=4)


def write_transcripts(transcripts_obj_list: YoutubeVideoTranscriptList) -> None:
    for transcript_obj in transcripts_obj_list.transcripts:
        write_transcript(transcript_obj)


def read_transcript(video_id: str) -> YoutubeVideoTranscript:
    transcript_file_path = TRANSCRIPTS_DATA_PATH / f"{video_id}.json"
    with open(transcript_file_path) as file:
        json_data = json.load(file)
    return YoutubeVideoTranscript.model_validate(json_data)


def read_transcripts() -> YoutubeVideoTranscriptList:
    transcripts_list = []
    for transcript_file_path in TRANSCRIPTS_DATA_PATH.rglob("*.json"):
        transcripts_list.append(read_transcript(transcript_file_path.stem))
    return YoutubeVideoTranscriptList(transcripts=transcripts_list)


def read_channels_state() -> YoutubeChannelList:
    with open(CHANNELS_STATE_FILE) as file:
        json_data = json.load(file)
    channels_obj_list = YoutubeChannelList.model_validate(json_data)
    return channels_obj_list


def is_new(video_id: str) -> bool:
    existing_video_ids = [file.stem for file in TRANSCRIPTS_DATA_PATH.rglob("*.json")]
    return video_id not in existing_video_ids


def read_summary(video_id: str, step: str):
    if step == "base":
        summary_path = BASE_SUMMARIES_DATA_PATH
    elif step == "user":
        summary_path = USER_SUMMARIES_DATA_PATH
    else:
        raise ValueError

    transcript_file_path = summary_path / f"{video_id}.json"
    with open(transcript_file_path) as file:
        json_data = json.load(file)
    return YoutubeVideoTranscript.model_validate(json_data)

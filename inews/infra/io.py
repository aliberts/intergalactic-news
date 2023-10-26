import json
from pathlib import Path

import boto3
import yaml

from inews.infra.models import ChannelList, Summary, Transcript, TranscriptList, VideoID

s3 = boto3.resource("s3")

BUCKET = "intergalactic-news"
CHANNELS_S3_FILE = "channels_state.json"
TRANSCRIPTS_S3_PATH = "transcripts/"
SUMMARIES_S3_PATH = "summaries/"

CHANNELS_ID_FILE = Path("config/channels_id.yaml")
CHANNELS_LOCAL_FILE = Path("data/channels_state.json")
TRANSCRIPTS_LOCAL_PATH = Path("data/transcripts/")
SUMMARIES_LOCAL_PATH = Path("data/summaries/")


def clear_bucket() -> None:
    bucket = s3.Bucket(BUCKET)
    to_delete = []
    for object in bucket.objects.all():
        if object.key.endswith("json"):
            to_delete.append({"Key": object.key})

    bucket.delete_objects(Delete={"Objects": to_delete})


def clear_local() -> None:
    CHANNELS_LOCAL_FILE.unlink()

    for transcript_file_path in TRANSCRIPTS_LOCAL_PATH.rglob("*.json"):
        transcript_file_path.unlink()

    for summary_file_path in SUMMARIES_LOCAL_PATH.rglob("*.json"):
        summary_file_path.unlink()


def pull_from_bucket() -> None:
    bucket = s3.Bucket(BUCKET)
    bucket.download_file(CHANNELS_S3_FILE, CHANNELS_LOCAL_FILE)

    for object in bucket.objects.filter(Prefix=TRANSCRIPTS_S3_PATH):
        if object.key.endswith("json"):
            local_file_name = Path(object.key).name
            local_file_path = TRANSCRIPTS_LOCAL_PATH / local_file_name
            bucket.download_file(object.key, local_file_path)

    for object in bucket.objects.filter(Prefix=SUMMARIES_S3_PATH):
        if object.key.endswith("json"):
            local_file_name = Path(object.key).name
            local_file_path = SUMMARIES_LOCAL_PATH / local_file_name
            bucket.download_file(object.key, local_file_path)


def push_to_bucket() -> None:
    bucket = s3.Bucket(BUCKET)
    bucket.upload_file(CHANNELS_LOCAL_FILE, CHANNELS_S3_FILE)

    for transcript_file_path in TRANSCRIPTS_LOCAL_PATH.rglob("*.json"):
        s3_file_path = TRANSCRIPTS_S3_PATH + transcript_file_path.name
        bucket.upload_file(transcript_file_path, s3_file_path)

    for summary_file_path in SUMMARIES_LOCAL_PATH.rglob("*.json"):
        s3_file_path = SUMMARIES_S3_PATH + summary_file_path.name
        bucket.upload_file(summary_file_path, s3_file_path)


def get_channels_id() -> list:
    with open(CHANNELS_ID_FILE) as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def write_channels_state(channels_list: ChannelList) -> None:
    with open(CHANNELS_LOCAL_FILE, "w") as file:
        json.dump(channels_list.model_dump(mode="json"), file, indent=4)


def read_channels_state() -> ChannelList:
    with open(CHANNELS_LOCAL_FILE) as file:
        json_data = json.load(file)
    return ChannelList.model_validate(json_data)


def write_transcript(transcript: Transcript) -> None:
    file_name = f"{transcript.video_id}.json"
    file_path = TRANSCRIPTS_LOCAL_PATH / file_name
    with open(file_path, "w") as file:
        json.dump(transcript.model_dump(mode="json"), file, indent=4)


def write_transcripts(transcripts_list: TranscriptList) -> None:
    for transcript in transcripts_list:
        write_transcript(transcript)


def read_transcript(video_id: VideoID) -> Transcript:
    transcript_file_path = TRANSCRIPTS_LOCAL_PATH / f"{video_id}.json"
    with open(transcript_file_path) as file:
        json_data = json.load(file)
    return Transcript.model_validate(json_data)


def read_transcripts(channels_list: ChannelList) -> TranscriptList:
    transcripts_list = []
    for channel in channels_list:
        for video in channel.recent_videos:
            transcripts_list.append(read_transcript(video.id))
    return TranscriptList.model_validate(transcripts_list)


def read_all_transcripts() -> TranscriptList:
    transcripts_list = []
    for transcript_file_path in TRANSCRIPTS_LOCAL_PATH.rglob("*.json"):
        transcripts_list.append(read_transcript(transcript_file_path.stem))
    return TranscriptList.model_validate(transcripts_list)


def is_new(video_id: VideoID) -> bool:
    existing_videos_id = [file.stem for file in TRANSCRIPTS_LOCAL_PATH.rglob("*.json")]
    return video_id not in existing_videos_id


def read_summary(video_id: VideoID) -> Summary:
    file_name = f"{video_id}.json"
    file_path = SUMMARIES_LOCAL_PATH / file_name
    with open(file_path) as file:
        json_data = json.load(file)
    return Summary.model_validate(json_data)


def write_summary(summary: Summary) -> None:
    file_name = f"{summary.infos.video_id}.json"
    file_path = SUMMARIES_LOCAL_PATH / file_name
    with open(file_path, "w") as file:
        json.dump(summary.model_dump(mode="json"), file, indent=4)

import json
import os
from pathlib import Path
from typing import Any

import boto3
import yaml
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from inews.infra.types import ChannelID, VideoInfoP

load_dotenv()

s3 = boto3.resource(
    "s3",
    region_name=os.environ["AWS_REGION"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
)

# S3
BUCKET = "intergalactic-news"
CHANNELS_S3_FILE = "channels_state.json"
TRANSCRIPTS_S3_PATH = "transcripts/"
SUMMARIES_S3_PATH = "summaries/"
STORIES_S3_PATH = "stories/"
ISSUES_S3_PATH = "issues/"

# Config
CHANNELS_ID_FILE = Path("config/channels_id.yaml")
DATA_CONFIG_FILE = Path("config/data.yaml")
MAILING_CONFIG_FILE = Path("config/mailing.yaml")

# Data
CHANNELS_LOCAL_FILE = Path("data/channels_state.json")
TRANSCRIPTS_LOCAL_PATH = Path("data/transcripts/")
SUMMARIES_LOCAL_PATH = Path("data/summaries/")
STORIES_LOCAL_PATH = Path("data/stories/")
NEWSLETTERS_LOCAL_PATH = Path("data/newsletters/")

# Html
HTML_TEMPLATE_PATH = Path("data/html/templates/")
HTML_BUILD_PATH = Path("data/html/build/")


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

    for story_file_path in STORIES_LOCAL_PATH.rglob("*.json"):
        story_file_path.unlink()

    for newsletter_file_path in NEWSLETTERS_LOCAL_PATH.rglob("*.json"):
        newsletter_file_path.unlink()

    for html_file_path in HTML_BUILD_PATH.rglob("*.html"):
        html_file_path.unlink()


def download_file_from_bucket(bucket, s3_path: str, local_path: Path) -> None:
    try:
        bucket.download_file(s3_path, local_path)
    except ClientError:
        return


def pull_data_from_bucket() -> None:
    bucket = s3.Bucket(BUCKET)
    download_file_from_bucket(bucket, CHANNELS_S3_FILE, CHANNELS_LOCAL_FILE)

    for object in bucket.objects.filter(Prefix=TRANSCRIPTS_S3_PATH):
        if object.key.endswith("json"):
            local_file_name = Path(object.key).name
            local_file_path = TRANSCRIPTS_LOCAL_PATH / local_file_name
            download_file_from_bucket(bucket, object.key, local_file_path)

    for object in bucket.objects.filter(Prefix=SUMMARIES_S3_PATH):
        if object.key.endswith("json"):
            local_file_name = Path(object.key).name
            local_file_path = SUMMARIES_LOCAL_PATH / local_file_name
            download_file_from_bucket(bucket, object.key, local_file_path)

    for object in bucket.objects.filter(Prefix=STORIES_S3_PATH):
        if object.key.endswith("json"):
            local_file_name = Path(object.key).name
            local_file_path = STORIES_LOCAL_PATH / local_file_name
            download_file_from_bucket(bucket, object.key, local_file_path)


def push_data_to_bucket() -> None:
    bucket = s3.Bucket(BUCKET)
    bucket.upload_file(CHANNELS_LOCAL_FILE, CHANNELS_S3_FILE)

    for transcript_file_path in TRANSCRIPTS_LOCAL_PATH.rglob("*.json"):
        s3_file_path = TRANSCRIPTS_S3_PATH + transcript_file_path.name
        bucket.upload_file(transcript_file_path, s3_file_path)

    for summary_file_path in SUMMARIES_LOCAL_PATH.rglob("*.json"):
        s3_file_path = SUMMARIES_S3_PATH + summary_file_path.name
        bucket.upload_file(summary_file_path, s3_file_path)

    for story_file_path in STORIES_LOCAL_PATH.rglob("*.json"):
        s3_file_path = STORIES_S3_PATH + story_file_path.name
        bucket.upload_file(story_file_path, s3_file_path)


def pull_issues_from_bucket() -> None:
    bucket = s3.Bucket(BUCKET)

    for object in bucket.objects.filter(Prefix=ISSUES_S3_PATH):
        if object.key.endswith("html"):
            local_file_name = Path(object.key).name
            local_file_path = HTML_BUILD_PATH / local_file_name
            download_file_from_bucket(bucket, object.key, local_file_path)


def push_issues_to_bucket() -> None:
    bucket = s3.Bucket(BUCKET)

    for issue_file_path in HTML_BUILD_PATH.rglob("*.html"):
        s3_file_path = ISSUES_S3_PATH + issue_file_path.name
        bucket.upload_file(issue_file_path, s3_file_path)


def get_data_config() -> dict:
    with open(DATA_CONFIG_FILE) as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def get_mailing_config() -> dict:
    with open(MAILING_CONFIG_FILE) as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def get_config_channel_ids() -> list[ChannelID]:
    with open(CHANNELS_ID_FILE) as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def get_file_name(video_info: VideoInfoP) -> Path:
    return Path(f"{video_info.date.date()}.{video_info.id}.json")


def video_in_local_files(video_info: VideoInfoP) -> bool:
    file_path = TRANSCRIPTS_LOCAL_PATH / get_file_name(video_info)
    return file_path.is_file()


def summary_in_local_files(video_info: VideoInfoP) -> bool:
    file_path = SUMMARIES_LOCAL_PATH / get_file_name(video_info)
    return file_path.is_file()


def story_in_local_files(video_info: VideoInfoP) -> bool:
    file_path = STORIES_LOCAL_PATH / get_file_name(video_info)
    return file_path.is_file()


def save_to_json_file(data: Any, file_path: Path) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def load_from_json_file(file_path: Path) -> Any:
    with open(file_path) as file:
        return json.load(file)


def read_html_template(template_name: str) -> str:
    file_path = HTML_TEMPLATE_PATH / f"{template_name}.html"
    with open(file_path) as file:
        html = file.read()
    return html


def save_to_html_file(html: str, file_path: Path) -> None:
    with open(file_path, "w") as file:
        html = file.write(html)

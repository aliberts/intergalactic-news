import json
import os
from pathlib import Path
from typing import Any

import boto3
import yaml
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from inews.infra.types import ChannelID, VideoID, VideoInfoP

load_dotenv()

session_token = os.environ["AWS_SESSION_TOKEN"] if "AWS_SESSION_TOKEN" in os.environ else None
s3 = boto3.resource(
    "s3",
    region_name=os.environ["AWS_REGION"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    aws_session_token=session_token,
)


# S3
CHANNELS_S3_FILE = "channels_state.json"
VIDEOS_S3_FILE = "videos_state.json"
STORIES_S3_PATH = "stories/"
NEWSLETTERS_S3_PATH = "newsletters/"
ISSUES_S3_PATH = "issues/"

# Config
CHANNELS_ID_FILE = Path("config/channels_id.yaml")
DATA_CONFIG_FILE = Path("config/data.yaml")
MAILING_CONFIG_FILE = Path("config/mailing.yaml")

# Data
DATA_PATH = Path("/tmp") if "AWS_LAMBDA_FUNCTION_NAME" in os.environ else Path("data")
CHANNELS_LOCAL_FILE = DATA_PATH / Path("channels_state.json")
VIDEOS_LOCAL_FILE = DATA_PATH / Path("videos_state.json")
TRANSCRIPTS_LOCAL_PATH = DATA_PATH / Path("transcripts/")
SUMMARIES_LOCAL_PATH = DATA_PATH / Path("summaries/")
STORIES_LOCAL_PATH = DATA_PATH / Path("stories/")
NEWSLETTERS_LOCAL_PATH = DATA_PATH / Path("newsletters/")

# Html
HTML_TEMPLATE_PATH = Path("inews/templates/")
HTML_BUILD_PATH = DATA_PATH / Path("html/")


def clear_bucket(bucket_name: str) -> None:
    bucket = s3.Bucket(bucket_name)
    to_delete = []
    for object in bucket.objects.all():
        if object.key.endswith("json"):
            to_delete.append({"Key": object.key})

    bucket.delete_objects(Delete={"Objects": to_delete})


def clear_local() -> None:
    for json_file_path in DATA_PATH.rglob("*.json"):
        json_file_path.unlink()

    for html_file_path in HTML_BUILD_PATH.rglob("*.html"):
        html_file_path.unlink()


def make_data_dirs():
    TRANSCRIPTS_LOCAL_PATH.mkdir(parents=True, exist_ok=True)
    SUMMARIES_LOCAL_PATH.mkdir(parents=True, exist_ok=True)
    STORIES_LOCAL_PATH.mkdir(parents=True, exist_ok=True)
    NEWSLETTERS_LOCAL_PATH.mkdir(parents=True, exist_ok=True)
    HTML_BUILD_PATH.mkdir(parents=True, exist_ok=True)


def download_file_from_bucket(bucket, s3_path: str, local_path: Path) -> None:
    try:
        bucket.download_file(s3_path, local_path)
        return 1
    except ClientError:
        return 0


def pull_data_from_bucket(bucket_name: str) -> None:
    files_count = 0
    bucket = s3.Bucket(bucket_name)
    files_count += download_file_from_bucket(bucket, CHANNELS_S3_FILE, CHANNELS_LOCAL_FILE)
    files_count += download_file_from_bucket(bucket, VIDEOS_S3_FILE, VIDEOS_LOCAL_FILE)

    for object in bucket.objects.filter(Prefix=STORIES_S3_PATH):
        if object.key.endswith("json"):
            local_file_name = Path(object.key).name
            local_file_path = STORIES_LOCAL_PATH / local_file_name
            files_count += download_file_from_bucket(bucket, object.key, local_file_path)

    print(f"Downloaded {files_count} data files from {bucket_name} bucket")


def push_data_to_bucket(bucket_name: str) -> None:
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file(CHANNELS_LOCAL_FILE, CHANNELS_S3_FILE)
    bucket.upload_file(VIDEOS_LOCAL_FILE, VIDEOS_S3_FILE)

    files_count = 2
    for story_file_path in STORIES_LOCAL_PATH.rglob("*.json"):
        s3_file_path = STORIES_S3_PATH + story_file_path.name
        bucket.upload_file(story_file_path, s3_file_path)
        files_count += 1

    print(f"Uploaded {files_count} data files to {bucket_name} bucket")


def push_newsletters_to_bucket(bucket_name: str) -> None:
    bucket = s3.Bucket(bucket_name)
    files_count = 0

    for newsletter_file_path in NEWSLETTERS_LOCAL_PATH.rglob("*.json"):
        s3_file_path = NEWSLETTERS_S3_PATH + newsletter_file_path.name
        bucket.upload_file(newsletter_file_path, s3_file_path)
        files_count += 1

    print(f"Uploaded {files_count} newsletter files to {bucket_name} bucket")


def pull_issues_from_bucket(bucket_name: str) -> None:
    bucket = s3.Bucket(bucket_name)

    for object in bucket.objects.filter(Prefix=ISSUES_S3_PATH):
        if object.key.endswith("html"):
            local_file_name = Path(object.key).name
            local_file_path = HTML_BUILD_PATH / local_file_name
            download_file_from_bucket(bucket, object.key, local_file_path)


def push_issues_to_bucket(bucket_name: str) -> None:
    bucket = s3.Bucket(bucket_name)

    for issue_file_path in HTML_BUILD_PATH.rglob("*.html"):
        s3_file_path = ISSUES_S3_PATH + issue_file_path.name
        bucket.upload_file(issue_file_path, s3_file_path)


def get_data_config() -> dict:
    with open(DATA_CONFIG_FILE, encoding="utf-8") as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def get_mailing_config() -> dict:
    with open(MAILING_CONFIG_FILE, encoding="utf-8") as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def get_config_channel_ids() -> list[ChannelID]:
    with open(CHANNELS_ID_FILE, encoding="utf-8") as file:
        channels_id = yaml.safe_load(file)
    return channels_id


def get_file_name(video_info: VideoInfoP) -> Path:
    return Path(f"{video_info.date.date()}.{video_info.id}.json")


def video_id_local_file(video_id: VideoID) -> Path | None:
    local_path = None
    for path in TRANSCRIPTS_LOCAL_PATH.rglob("*.json"):
        if video_id in path.name:
            local_path = path
    return local_path


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
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_from_json_file(file_path: Path) -> Any:
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def load_html_template(template_name: str) -> str:
    file_path = HTML_TEMPLATE_PATH / f"{template_name}.html"
    with open(file_path, encoding="utf-8") as file:
        html = file.read()
    return html


def save_to_html_file(html: str, file_path: Path) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        html = file.write(html)

from pathlib import Path

import boto3
import yaml

from inews.infra.types import VideoID

s3 = boto3.resource("s3")

BUCKET = "intergalactic-news"
CHANNELS_S3_FILE = "channels_state.json"
TRANSCRIPTS_S3_PATH = "transcripts/"
SUMMARIES_S3_PATH = "summaries/"

CHANNELS_ID_FILE = Path("config/channels_id.yaml")
CHANNELS_LOCAL_FILE = Path("data/channels_state.json")
TRANSCRIPTS_LOCAL_PATH = Path("data/transcripts/")
SUMMARIES_LOCAL_PATH = Path("data/summaries/")
HTML_TEMPLATE_PATH = Path("data/html_templates/")
HTML_PATH = Path("data/html/")


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


def is_new(video_id: VideoID) -> bool:
    candidates = list(TRANSCRIPTS_LOCAL_PATH.rglob(f"*.{video_id}.json"))
    return len(candidates) == 0


def read_html_template(template_name: str) -> str:
    file_path = HTML_TEMPLATE_PATH / f"{template_name}.html"
    with open(file_path) as file:
        html = file.read()
    return html


def write_html(html: str, file_name: str) -> None:
    file_path = HTML_PATH / f"{file_name}.html"
    with open(file_path, "w") as file:
        html = file.write(html)

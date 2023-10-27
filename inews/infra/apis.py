import os

import googleapiclient.discovery
import mailchimp_marketing
import openai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptAvailable,
    NoTranscriptFound,
    TranscriptsDisabled,
)

TranscriptError = (NoTranscriptAvailable, NoTranscriptFound, TranscriptsDisabled)

load_dotenv()

MAILCHIMP_SERVER_PREFIX = "us21"


def get_youtube():
    api_key = os.environ["GOOGLE_API_KEY"]
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
    return youtube


def get_yt_transcript():
    return YouTubeTranscriptApi


def get_openai():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai


def get_mailchimp():
    client = mailchimp_marketing.Client()
    client.set_config(
        {
            "api_key": os.environ["MAILCHIMP_API_KEY"],
            "server": MAILCHIMP_SERVER_PREFIX,
        }
    )
    members_list_id = os.environ["MAILCHIMP_MEMBERS_LIST_ID"]
    return client, members_list_id

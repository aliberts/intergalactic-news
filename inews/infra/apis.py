import os

import googleapiclient.discovery
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

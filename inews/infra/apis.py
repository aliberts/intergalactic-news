import os

import googleapiclient.discovery
from dotenv import load_dotenv


def setup_youtube_api_client():
    load_dotenv()
    api_key = os.environ["GOOGLE_API_KEY"]
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
    return youtube

import json
from pathlib import Path

import yaml
from unidecode import unidecode
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

from inews.domain import preprocessing
from inews.infra.apis import setup_youtube_api_client
from inews.infra.models import (
    YoutubeChannelList,
    YoutubeVideoTranscript,
    YoutubeVideoTranscriptList,
)

CHANNELS_ID_FILE = Path("config/channels_id.yaml")
CHANNELS_STATE_FILE = Path("data/channels_state.json")
TRANSCRIPTS_DATA_PATH = Path("data/transcripts/")

youtube = setup_youtube_api_client()


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


def read_channels_state() -> YoutubeChannelList:
    with open(CHANNELS_STATE_FILE) as file:
        json_data = json.load(file)
    channels_obj_list = YoutubeChannelList.model_validate(json_data)
    return channels_obj_list


def is_new(video_id: str) -> bool:
    existing_video_ids = [file.stem for file in TRANSCRIPTS_DATA_PATH.rglob("*.json")]
    return video_id not in existing_video_ids


def get_recent_videos(youtube, uploads_playlist_id, number_of_videos=3) -> list:
    max_results = 5 * number_of_videos
    request = youtube.playlistItems().list(
        part="snippet", maxResults=max_results, playlistId=uploads_playlist_id
    )
    response = request.execute()

    recent_videos_list = []
    for item in response["items"]:
        if "#shorts" in item["snippet"]["title"]:
            # HACK this is a workaround as there is currently no way of checking if
            # a video is a short or not with playlistItems and the hashtag "#shorts"
            # is not mandotory in youtube #shorts titles. Might not alway work.
            continue
        else:
            recent_videos_list.append(
                {
                    "id": item["snippet"]["resourceId"]["videoId"],
                    "title": unidecode(item["snippet"]["title"]),
                    "date": item["snippet"]["publishedAt"],
                }
            )
            if len(recent_videos_list) == number_of_videos:
                break

    return recent_videos_list


def initialize_channels_state():
    with open(CHANNELS_ID_FILE) as file:
        channels_id = yaml.safe_load(file)
    channels_list = []

    # get uploads playlist id
    request = youtube.channels().list(part="contentDetails, snippet", id=channels_id, maxResults=50)
    response = request.execute()
    for channel in response["items"]:
        channels_list.append(
            {
                "id": channel["id"],
                "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"],
                "name": channel["snippet"]["title"],
            }
        )

    # get last upload that are not youtube #shorts
    for channel in channels_list:
        channel["recent_videos"] = get_recent_videos(youtube, channel["uploads_playlist_id"])

    channels_obj_list = YoutubeChannelList(channels=channels_list)
    write_channels_state(channels_obj_list)

    return channels_obj_list


def get_transcripts(channels_obj_list: YoutubeChannelList) -> YoutubeVideoTranscriptList:
    transcripts_list = []
    for channel in channels_obj_list.channels:
        for video in channel.recent_videos:
            if is_new(video.id):
                try:
                    available_transcript = YouTubeTranscriptApi.list_transcripts(
                        video.id
                    ).find_transcript(["en"])
                except TranscriptsDisabled:
                    continue
                raw_transcript = available_transcript.fetch()
                transcript = preprocessing.format_transcript(raw_transcript)
                transcripts_list.append(
                    {
                        "video_id": video.id,
                        "video_title": video.title,
                        "channel_id": channel.id,
                        "channel_name": channel.name,
                        "date": video.date,
                        "is_generated": available_transcript.is_generated,
                        "transcript": transcript,
                    }
                )

    transcripts_obj_list = YoutubeVideoTranscriptList(transcripts=transcripts_list)
    write_transcripts(transcripts_obj_list)
    return transcripts_obj_list

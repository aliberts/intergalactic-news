from unidecode import unidecode
from youtube_transcript_api._transcripts import Transcript

from inews.infra import apis
from inews.infra.types import ChannelID, VideoID

youtube_api = apis.get_youtube()
yt_transcript_api = apis.get_yt_transcript()


def chunks(full_list: list, size: int = 50):
    for i in range(0, len(full_list), size):
        yield full_list[i : i + size]


def get_channels_info(channels_id: list[ChannelID]) -> list[dict]:
    if len(channels_id) == 0:
        return []

    request = youtube_api.channels().list(
        part="snippet,contentDetails", id=channels_id, maxResults=50
    )
    response = request.execute()
    channels_infos = []
    for item in response["items"]:
        channels_infos.append(
            {
                "id": item["id"],
                "name": item["snippet"]["title"],
                "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
            }
        )
    return channels_infos


def get_channel_recent_videos_ids(uploads_playlist_id: str, max_results: int = 50) -> list[VideoID]:
    request = youtube_api.playlistItems().list(
        part="snippet", maxResults=max_results, playlistId=uploads_playlist_id
    )
    response = request.execute()
    videos_id = [item["snippet"]["resourceId"]["videoId"] for item in response["items"]]
    return videos_id


def get_videos_info(videos_ids: list[VideoID]) -> list[dict]:
    response_items = []
    for videos_ids_chunk in chunks(videos_ids):
        request = youtube_api.videos().list(part="snippet,contentDetails", id=videos_ids_chunk)
        chunk_response = request.execute()
        response_items += chunk_response["items"]

    videos_info_list = []
    for item in response_items:
        videos_info_list.append(
            {
                "id": item["id"],
                "channel_id": item["snippet"]["channelId"],
                "title": unidecode(item["snippet"]["title"]),
                "date": item["snippet"]["publishedAt"],
                "duration": item["contentDetails"]["duration"],
                "thumbnail_url": item["snippet"]["thumbnails"]["medium"]["url"],
            }
        )
    return videos_info_list


def get_available_transcript(video_id: VideoID) -> Transcript | None:
    try:
        return yt_transcript_api.list_transcripts(video_id).find_transcript(["en"])
    except apis.TranscriptError:
        return None

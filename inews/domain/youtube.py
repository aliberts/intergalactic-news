from unidecode import unidecode
from youtube_transcript_api._transcripts import Transcript

from inews.infra import apis
from inews.infra.types import ChannelID, VideoID

youtube_api = apis.get_youtube()
yt_transcript_api = apis.get_yt_transcript()


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


def get_channel_recent_videos_id(uploads_playlist_id: str, max_results: int = 50) -> list[VideoID]:
    request = youtube_api.playlistItems().list(
        part="snippet", maxResults=max_results, playlistId=uploads_playlist_id
    )
    response = request.execute()
    videos_id = [item["snippet"]["resourceId"]["videoId"] for item in response["items"]]
    return videos_id


def get_videos_infos(videos_id: list[VideoID]) -> list[dict]:
    request = youtube_api.videos().list(part="snippet,contentDetails", id=videos_id)
    response = request.execute()
    video_infos = []
    for item in response["items"]:
        video_infos.append(
            {
                "id": item["id"],
                "title": unidecode(item["snippet"]["title"]),
                "date": item["snippet"]["publishedAt"],
                "duration": item["contentDetails"]["duration"],
                "thumbnail_url": item["snippet"]["thumbnails"]["medium"]["url"],
            }
        )
    return video_infos


def get_available_transcript(video_id: VideoID) -> Transcript | None:
    try:
        return yt_transcript_api.list_transcripts(video_id).find_transcript(["en"])
    except apis.TranscriptError:
        return None

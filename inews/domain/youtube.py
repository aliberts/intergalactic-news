from youtube_transcript_api._transcripts import Transcript

from inews.infra import apis
from inews.infra.types import VideoID

youtube_api = apis.get_youtube()
yt_transcript_api = apis.get_yt_transcript()


def get_channels_info(channels_id: list) -> dict:
    request = youtube_api.channels().list(
        part="snippet,contentDetails", id=channels_id, maxResults=50
    )
    return request.execute()


def get_channel_recent_videos_id(uploads_playlist_id: str, max_results: int = 50) -> dict:
    request = youtube_api.playlistItems().list(
        part="snippet", maxResults=max_results, playlistId=uploads_playlist_id
    )
    return request.execute()


def get_videos_infos(videos_id: list[VideoID]) -> dict:
    request = youtube_api.videos().list(part="snippet,contentDetails", id=videos_id)
    return request.execute()


def get_available_transcript(video_id: VideoID) -> Transcript | None:
    try:
        return yt_transcript_api.list_transcripts(video_id).find_transcript(["en"])
    except apis.TranscriptError:
        return None

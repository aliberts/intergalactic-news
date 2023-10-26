from unidecode import unidecode

from inews.domain import preprocessing
from inews.infra import apis, io
from inews.infra.models import Channel, ChannelList, Transcript, TranscriptList, Video, VideoID

youtube_api = apis.get_youtube()
yt_transcript_api = apis.get_yt_transcript()


def get_channels_info(channels_id: list) -> ChannelList:
    request = youtube_api.channels().list(
        part="snippet,contentDetails", id=channels_id, maxResults=50
    )
    response = request.execute()

    channels = []
    for channel in response["items"]:
        channels.append(
            Channel(
                **{
                    "id": channel["id"],
                    "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"],
                    "name": channel["snippet"]["title"],
                    "recent_videos": [],
                }
            )
        )
    return ChannelList.model_validate(channels)


def get_channel_recent_videos_id(channel: Channel, number_of_videos: int = 3) -> list[VideoID]:
    max_results = 5 * number_of_videos
    request = youtube_api.playlistItems().list(
        part="snippet", maxResults=max_results, playlistId=channel.uploads_playlist_id
    )
    response = request.execute()

    videos_id = []
    for item in response["items"]:
        videos_id.append(item["snippet"]["resourceId"]["videoId"])

    return videos_id


def get_videos_info(videos_id: list[VideoID]) -> list[Video]:
    request = youtube_api.videos().list(part="snippet,contentDetails", id=videos_id)
    response = request.execute()

    videos = []
    for item in response["items"]:
        videos.append(
            Video(
                **{
                    "id": item["id"],
                    "title": unidecode(item["snippet"]["title"]),
                    "date": item["snippet"]["publishedAt"],
                    "duration": item["contentDetails"]["duration"],
                }
            )
        )
    return videos


def get_available_transcript(video_id: VideoID):
    try:
        return yt_transcript_api.list_transcripts(video_id).find_transcript(["en"])
    except apis.TranscriptError:
        return None


def get_transcripts(channels_list: ChannelList) -> TranscriptList:
    transcripts = []
    for channel in channels_list:
        for video in channel.recent_videos:
            if io.is_new(video.id):
                available_transcript = get_available_transcript(video.id)
                if available_transcript is not None:
                    raw_transcript = available_transcript.fetch()
                else:
                    continue
                transcript = preprocessing.format_transcript(raw_transcript)
                tokens_count = preprocessing.count_tokens(transcript)
                transcripts.append(
                    Transcript(
                        **{
                            "channel_id": channel.id,
                            "channel_name": channel.name,
                            "video_id": video.id,
                            "video_title": video.title,
                            "date": video.date,
                            "duration": video.duration,
                            "is_generated": available_transcript.is_generated,
                            "tokens_count": tokens_count,
                            "transcript": transcript,
                        }
                    )
                )

    return TranscriptList.model_validate(transcripts)

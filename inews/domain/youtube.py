from unidecode import unidecode

from inews.domain import preprocessing
from inews.infra import apis, io
from inews.infra.models import YoutubeChannelList, YoutubeVideoTranscriptList

youtube_api = apis.get_youtube()


def get_recent_videos(uploads_playlist_id, number_of_videos=3) -> list:
    max_results = 5 * number_of_videos
    request = youtube_api.playlistItems().list(
        part="snippet", maxResults=max_results, playlistId=uploads_playlist_id
    )
    response = request.execute()

    recent_videos_list = []
    for item in response["items"]:
        if "#shorts" in item["snippet"]["title"]:
            # HACK this is a workaround as there is currently no way of checking if
            # a video is a short or not with playlistItems and the hashtag "#shorts"
            # is not mandotory in youtube #shorts titles. Might not always work.
            # TODO use videos().list to check duration of video is > 1mn
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
    channels_id = io.get_channels_id()
    channels_list = []

    # get uploads playlist id
    request = youtube_api.channels().list(
        part="contentDetails, snippet", id=channels_id, maxResults=50
    )
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
        channel["recent_videos"] = get_recent_videos(channel["uploads_playlist_id"])

    channels_obj_list = YoutubeChannelList(channels=channels_list)
    io.write_channels_state(channels_obj_list)

    return channels_obj_list


def get_transcripts(channels_obj_list: YoutubeChannelList) -> YoutubeVideoTranscriptList:
    yt_transcript_api = apis.get_yt_transcript()
    transcripts_list = []
    for channel in channels_obj_list.channels:
        for video in channel.recent_videos:
            if io.is_new(video.id):
                try:
                    available_transcript = yt_transcript_api.list_transcripts(
                        video.id
                    ).find_transcript(["en"])
                except apis.TranscriptError:
                    continue
                raw_transcript = available_transcript.fetch()
                transcript = preprocessing.format_transcript(raw_transcript)
                tokens_count = preprocessing.count_tokens(transcript)
                transcripts_list.append(
                    {
                        "video_id": video.id,
                        "video_title": video.title,
                        "channel_id": channel.id,
                        "channel_name": channel.name,
                        "date": video.date,
                        "is_generated": available_transcript.is_generated,
                        "tokens_count": tokens_count,
                        "transcript": transcript,
                    }
                )

    transcripts_obj_list = YoutubeVideoTranscriptList(transcripts=transcripts_list)
    io.write_transcripts(transcripts_obj_list)
    return transcripts_obj_list

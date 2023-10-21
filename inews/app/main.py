from youtube_transcript_api import YouTubeTranscriptApi

from inews.domain import preprocessing, youtube
from inews.infra.models import YoutubeVideoList

initialize = False


def main():
    if initialize:
        channels_obj_list = youtube.initialize_channels_state()
    else:
        channels_obj_list = youtube.read_channels_state()

    # TODO: check if last video is new, then get the transcript if it is

    videos_id = [channel.last_video_id for channel in channels_obj_list.channels]

    raw_transcripts, _ = YouTubeTranscriptApi.get_transcripts(videos_id, languages=["en"])

    transcripts = preprocessing.format_transcripts(raw_transcripts)

    video_list = []
    for channel in channels_obj_list.channels:
        video_id = channel.last_video_id
        video_list.append(
            {
                "id": video_id,
                "title": channel.last_video_title,
                "date": channel.last_video_date,
                "en_transcript": transcripts[video_id],
            }
        )

    videos_obj_list = YoutubeVideoList(videos=video_list)
    youtube.write_transcripts(videos_obj_list)


if __name__ == "__main__":
    main()

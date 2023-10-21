import json

from inews.infra.apis import setup_youtube_api_client
from inews.infra.models import YoutubeChannelList

CHANNELS_ID_NAME = {
    "UC7_gcs09iThXybpVgjHZ_7g": "PBS Space Time",
    "UCYNbYGl89UUowy8oXkipC-Q": "Dr. Becky",
    "UCciQ8wFcVoIIMi-lfu8-cjQ": "Anton Petrov",
    "UCIBaDdAbGlFDeS33shmlD0A": "European Space Agency, ESA",
    "UCxzC4EngIsMrPmbm6Nxvb-A": "Scott Manley",
}
CHANNELS_STATE_FILE = "inews/data/channels_state.json"
TRANSCRIPTS_FILE = "inews/data/transcripts.json"


def write_channels_state(channels_obj_list):
    with open(CHANNELS_STATE_FILE, "w") as file:
        json.dump(channels_obj_list.model_dump(mode="json"), file, indent=4)


def write_transcripts(videos_obj_list):
    with open(TRANSCRIPTS_FILE, "w") as file:
        json.dump(videos_obj_list.model_dump(mode="json"), file, indent=4)


def read_channels_state():
    with open(CHANNELS_STATE_FILE) as file:
        json_data = json.load(file)
    channels_obj_list = YoutubeChannelList.model_validate(json_data)
    return channels_obj_list


def initialize_channels_state():
    youtube = setup_youtube_api_client()

    channels_id = list(CHANNELS_ID_NAME.keys())
    channels_list = []

    # get uploads playlist id
    request = youtube.channels().list(part="contentDetails", id=channels_id, maxResults=50)
    response = request.execute()
    for channel in response["items"]:
        id = channel["id"]
        uploads_playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        channels_list.append(
            {
                "id": id,
                "uploads_playlist_id": uploads_playlist_id,
                "name": CHANNELS_ID_NAME[id],
            }
        )

    # get last upload that are not youtube #shorts
    for channel in channels_list:
        request = youtube.playlistItems().list(
            part="snippet", maxResults=10, playlistId=channel["uploads_playlist_id"]
        )
        response = request.execute()

        for item in response["items"]:
            if "#shorts" in item["snippet"]["title"]:
                # HACK this is a workaround as there is currently no way of checking if
                # a video is short or not, and the hashtag "#shorts" is not mandotory
                # in youtube #shorts titles. Might not alway work.
                continue
            else:
                channel["last_video_id"] = item["snippet"]["resourceId"]["videoId"]
                channel["last_video_kind"] = item["snippet"]["resourceId"]["kind"]
                channel["last_video_date"] = item["snippet"]["publishedAt"]
                channel["last_video_title"] = item["snippet"]["title"]
                break

    channels_obj_list = YoutubeChannelList(channels=channels_list)
    write_channels_state(channels_obj_list)

    return channels_obj_list


def get_transcripts(videos_obj_list):
    pass

import json
import os
from dataclasses import asdict
from pprint import pprint

import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv

from inews.infra.channels import yt_channels

load_dotenv()
api_key = os.environ["GOOGLE_API_KEY"]
api_service_name = "youtube"
api_version = "v3"


def main():
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

    id_list = [channel.id for channel in yt_channels.values()]

    request = youtube.channels().list(part="contentDetails", id=id_list, maxResults=50)
    response = request.execute()
    # pprint(response)

    for item in response["items"]:
        id = item["id"]
        yt_channels[id].uploads_playlist_id = item["contentDetails"]["relatedPlaylists"]["uploads"]

    channels_state = {}
    for channel in yt_channels.values():
        channels_state[channel.id] = asdict(channel)

    with open("inews/infra/channels_state.json", "w") as fp:
        json.dump(channels_state, fp, indent=4)

    for channel in yt_channels.values():
        request = youtube.playlistItems().list(
            part="contentDetails", maxResults=10, playlistId=channel.uploads_playlist_id
        )
        response = request.execute()
        pprint(response)


if __name__ == "__main__":
    main()

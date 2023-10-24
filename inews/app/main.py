from inews.domain import youtube
from inews.infra import io

initialize = True


def main():
    if initialize:
        channels_obj_list = youtube.initialize_channels_state()
    else:
        channels_obj_list = io.read_channels_state()

    youtube.get_transcripts(channels_obj_list)


if __name__ == "__main__":
    main()

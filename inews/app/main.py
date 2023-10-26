from inews.domain import openai, youtube
from inews.infra import io

initialize = True
# initialize = False


def main():
    if initialize:
        channels_list = youtube.initialize_channels_state()
        transcripts_list = youtube.get_transcripts(channels_list)
    else:
        channels_list = io.read_channels_state()
        transcripts_list = io.read_available_transcripts()

    openai.build_summaries(transcripts_list)


if __name__ == "__main__":
    main()

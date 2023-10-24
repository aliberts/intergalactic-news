from inews.domain import openai, youtube
from inews.infra import io

# initialize = True
initialize = False


def main():
    if initialize:
        channels_obj_list = youtube.initialize_channels_state()
        transcripts_obj_list = youtube.get_transcripts(channels_obj_list)
    else:
        channels_obj_list = io.read_channels_state()
        transcripts_obj_list = io.read_transcripts()

    transcripts_obj_list.transcripts = [transcripts_obj_list.transcripts[0]]
    openai.get_base_summaries(transcripts_obj_list)


if __name__ == "__main__":
    main()

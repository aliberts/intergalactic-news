from inews.domain import openai, youtube
from inews.infra import io
from inews.infra.models import User

# initialize = True
initialize = False


def main():
    if initialize:
        channels_list = youtube.initialize_channels_state()
        transcripts_list = youtube.get_transcripts(channels_list)
    else:
        channels_list = io.read_channels_state()
        transcripts_list = io.read_transcripts()

    summary_list = openai.get_base_summaries(transcripts_list)
    user = User(age=21, science_level="an expert")
    openai.get_user_summaries(summary_list, user)


if __name__ == "__main__":
    main()

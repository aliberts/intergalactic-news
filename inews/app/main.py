from inews.domain import pipeline
from inews.infra import io

# initialize = True
initialize = False


def main():
    if initialize:
        channels = pipeline.build_channels()
        transcripts = pipeline.build_transcripts(channels)
    else:
        channels = io.read_channels_state()
        transcripts = io.read_transcripts(channels)

    pipeline.build_summaries(transcripts)


if __name__ == "__main__":
    main()

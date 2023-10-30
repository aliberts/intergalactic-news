from inews.domain import pipeline


def main():
    channels = pipeline.build_channels(initialize=True)
    transcripts = pipeline.build_transcripts(channels, initialize=True)
    summaries = pipeline.build_summaries(transcripts, initialize=True)

    _ = pipeline.build_newsletters(summaries)


if __name__ == "__main__":
    main()

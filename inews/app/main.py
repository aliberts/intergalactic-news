from inews.domain import pipeline


def main():
    # getting channels
    channels = pipeline.build_channels(from_file=True)
    channels.update_last_week_videos()
    channels.save()

    # getting transcripts
    videos = pipeline.build_videos(channels, from_file=True)
    videos.get_available_transcripts()
    videos.drop_no_transcripts()
    videos.save()

    # getting summaries
    summaries = pipeline.build_summaries(videos, from_file=True)
    summaries.get_all(videos)
    summaries.save()

    # summaries = pipeline.select_stories(summaries)

    # _ = pipeline.build_newsletters(summaries)


if __name__ == "__main__":
    main()

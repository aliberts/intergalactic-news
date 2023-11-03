from inews.domain.models import ChannelList, Newsletter, StoryList, SummaryList, VideoList
from inews.infra import io

data_config = io.get_data_config()


def build_channels(from_file: bool = True) -> ChannelList:
    if from_file:
        channels = ChannelList.init_from_file()
    else:
        channels_id = io.get_channels_id()
        channels = ChannelList.init_from_api_with_ids(channels_id)
    return channels


def main():
    # getting channels
    channels = build_channels(from_file=True)
    # channels.update_recent_videos()
    channels.save()

    # getting transcripts
    videos = VideoList.init_from_channels(channels, use_local_files=True)
    videos.get_available_transcripts()
    videos.drop_no_transcripts()
    videos.save()

    # getting base summaries
    summaries = SummaryList.init_from_videos(videos, use_local_files=True)
    summaries.get_bases_from_videos(videos)
    summaries.get_topics()
    summaries.save()

    # # selecting stories
    summaries.drop_irrelevants()
    stories = StoryList.init_from_summaries(summaries, use_local_files=True)
    # stories = StoryList.init_from_all_files()
    stories.save()

    # # getting the rest of the content
    stories.get_shorts_from_summaries(summaries)
    stories.get_titles_from_summaries(summaries)
    stories.get_user_groups_from_summaries(summaries)
    stories.save()

    for group_id in data_config["user_groups"]:
        newsletter = Newsletter.init_from_summaries(group_id, stories)
        newsletter.make_html()
        newsletter.save()


if __name__ == "__main__":
    main()

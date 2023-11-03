from pathlib import Path

from tqdm import tqdm

from inews.domain import llm
from inews.domain.models import Channels, Newsletter, Story, Summary, Video
from inews.infra import io

data_config = io.get_data_config()


def build_videos_from_channels(channels: Channels, use_local_files: bool = True) -> list[Video]:
    videos = []
    for channel in channels:
        for video_info in channel.recent_videos:
            if io.video_in_local_files(video_info) and use_local_files:
                videos.append(Video.init_from_file(video_info))
            else:
                videos.append(Video(info=video_info, channel_info=channel.info))
    return videos


def build_summaries_from_videos(videos: list[Video], use_local_files: bool = True) -> list[Summary]:
    summaries = []
    for video in videos:
        if io.summary_in_local_files(video.info) and use_local_files:
            summaries.append(Summary.init_from_file(video.info))
        else:
            summaries.append(Summary(video_info=video.info, channel_info=video.channel_info))
    return summaries


def build_stories_from_summaries(
    summaries: list[Summary], use_local_files: bool = True
) -> list[Story]:
    stories = []
    for summary in summaries:
        if io.summary_in_local_files(summary.video_info) and use_local_files:
            stories.append(Story.init_from_file(summary.video_info))
        else:
            stories.append(Story(video_info=summary.video_info, channel_info=summary.channel_info))
    return stories


def get_stories_from_data_folder(data_folder: Path) -> list[Story]:
    stories = []
    for file_path in data_folder.rglob("*.json"):
        json_data = io.load_from_json_file(file_path)
        story = Story.model_validate(json_data)
        story.allow_requests = False
        stories.append(story)
    return stories


def select_relevant_summaries(summaries: list[Summary]) -> list[Summary]:
    selection = llm.get_stories_selection_from_topics(summaries)
    try:
        relevant_summaries = [
            summary
            for (summary, include) in zip(summaries, selection, strict=False)
            if include == "yes"
        ]
    except ValueError:
        Warning("Stories could not be selected, every story will be included.")
        relevant_summaries = summaries

    return relevant_summaries


def run_data():
    channels = Channels.init_from_file(io.CHANNELS_LOCAL_FILE)
    channels.update_recent_videos()
    channels.save()

    videos = build_videos_from_channels(channels, use_local_files=True)
    print("Getting transcripts")
    for video in tqdm(videos):
        video.get_available_transcript()

    videos = [video for video in videos if video.transcript is not None]
    for video in videos:
        video.save()

    summaries = build_summaries_from_videos(videos, use_local_files=True)
    print("Getting summaries")
    for summary, video in tqdm(zip(summaries, videos, strict=True)):
        summary.get_base_from_video(video)
        summary.save()

        summary.get_topics()
        summary.save()

    print("Selecting relevant stories")
    summaries = select_relevant_summaries(summaries)
    stories = build_stories_from_summaries(summaries, use_local_files=True)

    print("Building stories")
    for story, summary in tqdm(zip(stories, summaries, strict=True)):
        story.get_short_from_summary(summary)
        story.save()
        story.get_title_from_summary(summary)
        story.save()
        story.get_user_groups_from_summary(summary)
        story.save()


def run_newsletter():
    stories = get_stories_from_data_folder(io.STORIES_LOCAL_PATH)
    newsletter_summary = llm.get_newsletter_summary(stories)
    print(newsletter_summary)

    for group_id in data_config["user_groups"]:
        newsletter = Newsletter(group_id=group_id, stories=stories, summary=newsletter_summary)
        newsletter.build_html()
        newsletter.save()


def run_mailing():
    ...  # TODO

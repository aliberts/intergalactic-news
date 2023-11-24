import warnings
from pathlib import Path

import pendulum
from tqdm import tqdm

from inews.domain import llm
from inews.domain.models import (
    Channels,
    MCCampaign,
    Newsletter,
    NewsletterInfo,
    Story,
    Summary,
    Video,
)
from inews.infra import io
from inews.infra.types import RunStatus

data_config = io.get_data_config()


def run_data(status: RunStatus):
    io.make_data_dirs()
    io.pull_data_from_bucket()

    channels = build_channels(use_local_files=True)
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

    io.push_data_to_bucket()


def run_mailing(status: RunStatus):
    timezone = data_config["timezone"]
    today = pendulum.today(tz=timezone)

    if today.day_of_week != data_config["send_weekday"] and status is RunStatus.PROD:
        return

    newsletters = build_newsletters(today, status)

    if status is RunStatus.TEST:
        newsletters = [newsletters[0]]

    print("Sending newsletters")
    for newsletter in tqdm(newsletters):
        mc_campaign = MCCampaign.init_from_newsletter(newsletter)
        mc_campaign.create()
        mc_campaign.set_html()

        if status is RunStatus.TEST:
            mc_campaign.send_test()
        else:
            mc_campaign.send()

    io.push_issues_to_bucket()


def build_newsletters(today: pendulum.DateTime, status: RunStatus) -> list[Newsletter]:
    stories = get_stories_from_data_folder(io.STORIES_LOCAL_PATH)
    stories.sort(key=lambda x: x.video_info.date, reverse=True)

    if status is RunStatus.TEST:
        summary = "This is a summary"
    else:
        print("Getting newsletter summary")
        summary = llm.get_newsletter_summary(stories)

    newsletter_info = NewsletterInfo(date=today, summary=summary, stories=stories)
    newsletter_info.save()

    print("Building all newsletter versions")
    newsletters = []
    for group_id in tqdm(data_config["user_groups"]):
        read_time = newsletter_info.read_times[group_id]
        newsletter = Newsletter(info=newsletter_info, group_id=group_id, read_time=read_time)
        newsletter.build_html()
        newsletter.save_html_build()
        newsletters.append(newsletter)

    return newsletters


def select_relevant_summaries(summaries: list[Summary]) -> list[Summary]:
    selection = llm.get_stories_selection_from_topics(summaries)

    try:
        relevant_summaries = [
            summary
            for (summary, include) in zip(summaries, selection, strict=False)
            if include == "yes"
        ]
        if len(selection) < len(summaries):
            warnings.warn(
                "Story selection incomplete, some stories could be missing.", stacklevel=1
            )

    except ValueError:
        warnings.warn("Stories could not be selected, every story will be included.", stacklevel=1)
        relevant_summaries = summaries

    return relevant_summaries


def build_channels(use_local_files: bool = True) -> Channels:
    config_channel_ids = io.get_config_channel_ids()
    if io.CHANNELS_LOCAL_FILE.is_file() and use_local_files:
        channels = Channels.init_from_file(io.CHANNELS_LOCAL_FILE)
        channels.get_new_channels(config_channel_ids)
    else:
        channels = Channels.init_from_api_with_ids(config_channel_ids)
    return channels


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
        if io.story_in_local_files(summary.video_info) and use_local_files:
            stories.append(Story.init_from_file(summary.video_info))
        else:
            stories.append(Story(video_info=summary.video_info, channel_info=summary.channel_info))
    return stories


def get_stories_from_data_folder(data_folder: Path) -> list[Story]:
    stories = []
    for file_path in data_folder.rglob("*.json"):
        json_data = io.load_from_json_file(file_path)
        story = Story.model_validate(json_data)
        if story.is_too_old():
            continue
        story.allow_requests = False
        stories.append(story)
    return stories

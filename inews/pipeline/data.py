import copy
import warnings

from inews.domain import llm, youtube
from inews.domain.models import (
    ChannelInfo,
    Story,
    Summary,
    Video,
    VideoInfo,
)
from inews.infra import io
from inews.infra.types import ChannelID, RunEvent


def run(event: RunEvent):
    io.make_data_dirs()

    bucket_name = f"inews-{event.stage._value_}"
    if event.pull_from_bucket:
        io.pull_data_from_bucket(bucket_name)

    channels_ids = io.get_config_channel_ids()
    channels_state = build_channels_state(channels_ids)
    save_channels_state(channels_state)

    videos_state = build_videos_state(channels_state)
    for vinfo in videos_state:
        vinfo.use = vinfo.use and vinfo.is_valid
    save_videos_state(videos_state)

    videos = build_videos_from_state(videos_state, channels_state)

    transcripts_search = [video for video in videos if video.allow_requests]
    print(f"Searching transcripts for {len(transcripts_search)} videos")
    for video in videos:
        video.get_available_transcript()

    transcripts_found = [
        video for video in videos if video.transcript is not None and video.allow_requests
    ]
    print(f"Found {len(transcripts_found)} transcripts")

    for video in videos:
        video.info.use = video.info.use and video.valid_transcript

    videos_info = [video.info for video in videos]
    videos_state = update_videos_state(videos_state, videos_info)
    save_videos_state(videos_state)

    videos = [video for video in videos if video.info.use]
    for video in videos:
        video.save()
    print(f"Transcripts saved: {len(videos)} items")

    summaries = build_summaries_from_videos(videos, use_local_files=True)
    print(f"Getting summaries for {len(summaries)} transcripts")
    for summary, video in zip(summaries, videos, strict=True):
        summary.get_base_from_video(video, event)
        summary.get_topics(event)
        summary.save()
    print(f"Summaries saved: {len(summaries)} items")

    print("Selecting relevant stories")
    summaries_selected = select_relevant_summaries(summaries, event)
    selected_ids = [summary.video_info.id for summary in summaries_selected]
    for summary in summaries:
        summary.video_info.use = summary.video_info.use and summary.video_info.id in selected_ids

    videos_info = [summary.video_info for summary in summaries]
    videos_state = update_videos_state(videos_state, videos_info)
    save_videos_state(videos_state)

    print("Building stories")
    stories = build_stories_from_summaries(summaries_selected, use_local_files=True)
    for story, summary in zip(stories, summaries_selected, strict=True):
        story.get_short_from_summary(summary, event)
        story.get_title_from_summary(summary, event)
        story.get_user_groups_from_summary(summary, event)
        story.save()
    print(f"Stories saved: {len(stories)} items")

    if event.push_to_bucket:
        io.push_data_to_bucket(bucket_name)


def build_channels_state(channels_ids: list[ChannelID]) -> list[ChannelInfo]:
    previous_channels = []
    previous_ids = []
    if io.CHANNELS_LOCAL_FILE.is_file():
        channels_local_file = io.load_from_json_file(io.CHANNELS_LOCAL_FILE)
        previous_channels = [
            ChannelInfo(**cinfo) for cinfo in channels_local_file if cinfo["id"] in channels_ids
        ]
        previous_ids = [cinfo.id for cinfo in previous_channels]

    new_channels = []
    new_ids = [id for id in channels_ids if id not in previous_ids]
    if len(new_ids) > 0:
        channels_dicts = youtube.get_channels_info(new_ids)
        new_channels = [ChannelInfo.model_validate(_dict) for _dict in channels_dicts]

    print(f"Channels State: {len(channels_ids)} items")
    print(f"    > {len(new_channels)} items fetched from api")
    print(f"    > {len(previous_channels)} items read read from file")
    return previous_channels + new_channels


def build_videos_state(channels: list[ChannelInfo]) -> list[VideoInfo]:
    recent_videos_ids = []
    for channel in channels:
        ids = youtube.get_channel_recent_videos_ids(channel.uploads_playlist_id, max_results=15)
        recent_videos_ids += ids

    previous_videos = []
    previous_ids = []
    if io.VIDEOS_LOCAL_FILE.is_file():
        videos_local_file = io.load_from_json_file(io.VIDEOS_LOCAL_FILE)
        previous_videos = [
            VideoInfo(**vinfo) for vinfo in videos_local_file if vinfo["id"] in recent_videos_ids
        ]
        previous_ids = [vinfo.id for vinfo in previous_videos]

    new_videos = []
    new_ids = [id for id in recent_videos_ids if id not in previous_ids]
    if len(new_ids) > 0:
        videos_dicts = youtube.get_videos_info(new_ids)
        new_videos = [VideoInfo.model_validate(_dict) for _dict in videos_dicts]

    print(f"Videos State: {len(recent_videos_ids)} items")
    print(f"    > {len(new_videos)} items fetched from api")
    print(f"    > {len(previous_videos)} items read from file")
    return previous_videos + new_videos


def save_channels_state(channels_state: list[ChannelInfo]) -> None:
    io.save_to_json_file(
        [vinfo.model_dump(mode="json") for vinfo in channels_state], io.CHANNELS_LOCAL_FILE
    )
    print("Channels State saved")


def save_videos_state(videos_state: list[VideoInfo]) -> None:
    io.save_to_json_file(
        [vinfo.model_dump(mode="json") for vinfo in videos_state], io.VIDEOS_LOCAL_FILE
    )
    print("Videos State saved")


def update_videos_state(videos_state: list[VideoInfo], videos: list[VideoInfo]) -> list[VideoInfo]:
    new_videos_state = copy.deepcopy(videos_state)
    id_to_idx = {vinfo.id: idx for idx, vinfo in enumerate(videos_state)}
    for vinfo in videos:
        idx = id_to_idx[vinfo.id]
        new_videos_state[idx].use = vinfo.use

    valid_videos = [vinfo for vinfo in videos_state if vinfo.use]
    print(f"Videos State updated: {len(videos_state)} items")
    print(f"    > {len(valid_videos)} valid videos")
    return new_videos_state


def build_videos_from_state(
    videos_state: list[VideoInfo], channels_state: list[ChannelInfo]
) -> list[Video]:
    videos_info = [
        video for video in videos_state if video.use and not io.story_in_local_files(video)
    ]
    channels_info = {channel.id: channel for channel in channels_state}

    videos = []
    read_from_file = 0
    initialized = 0
    for video_info in videos_info:
        if io.video_in_local_files(video_info):
            videos.append(Video.init_from_file(video_info))
            read_from_file += 1
        else:
            channel_info = channels_info[video_info.channel_id]
            videos.append(Video(info=video_info, channel_info=channel_info))
            initialized += 1

    print(f"Videos built from state: {len(videos)} items")
    print(f"    > {initialized} items initialized")
    print(f"    > {read_from_file} items read from file")
    return videos


def build_summaries_from_videos(videos: list[Video], use_local_files: bool = True) -> list[Summary]:
    summaries = []
    read_from_file = 0
    initialized = 0
    for video in videos:
        if io.summary_in_local_files(video.info) and use_local_files:
            summaries.append(Summary.init_from_file(video.info))
            read_from_file += 1
        else:
            summaries.append(Summary(video_info=video.info, channel_info=video.channel_info))
            initialized += 1

    print(f"Summaries built from videos: {len(summaries)} items")
    print(f"    > {initialized} items initialized")
    print(f"    > {read_from_file} items read from file")
    return summaries


def select_relevant_summaries(summaries: list[Summary], event: RunEvent) -> list[Summary]:
    if len(summaries) == 0:
        return []

    selection = llm.get_stories_selection_from_topics(summaries, event)

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

    print(f"Summaries selected: {len(relevant_summaries)} items")
    return relevant_summaries


def build_stories_from_summaries(
    summaries: list[Summary], use_local_files: bool = True
) -> list[Story]:
    stories = []
    read_from_file = 0
    initialized = 0
    for summary in summaries:
        if io.story_in_local_files(summary.video_info) and use_local_files:
            stories.append(Story.init_from_file(summary.video_info))
            read_from_file += 1
        else:
            stories.append(Story(video_info=summary.video_info, channel_info=summary.channel_info))
            initialized += 1

    print(f"Stories built from summaries: {len(stories)} items")
    print(f"    > {initialized} items initialized")
    print(f"    > {read_from_file} items read from file")
    return stories

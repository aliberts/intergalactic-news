from pathlib import Path

import pendulum

from inews.domain import llm
from inews.domain.models import MCCampaign, Newsletter, NewsletterInfo, Story
from inews.infra import io
from inews.infra.types import RunEvent

mailing_config = io.get_mailing_config()


def run(event: RunEvent):
    timezone = mailing_config["timezone"]
    today = pendulum.today(tz=timezone)

    if today.day_of_week != mailing_config["send_weekday"] and not event.debug:
        return

    newsletters = build_newsletters(today, event)

    if not (event.send or event.send_test):
        return

    if event.debug:
        newsletters = [newsletters[0]]

    print("Sending newsletters")
    for newsletter in newsletters:
        mc_campaign = MCCampaign.init_from_newsletter(newsletter)
        mc_campaign.create()
        mc_campaign.set_html()

        if event.send:
            mc_campaign.send()

        if event.send_test:
            mc_campaign.send_test()

    if event.push_to_bucket:
        bucket_name = f"inews-{event.stage._value_}"
        io.push_issues_to_bucket(bucket_name)


def build_newsletters(today: pendulum.DateTime, event: RunEvent) -> list[Newsletter]:
    stories = get_stories_from_data_folder(io.STORIES_LOCAL_PATH)
    stories.sort(key=lambda x: x.video_info.date, reverse=True)

    print("Getting newsletter summary")
    summary = llm.get_newsletter_summary(stories, event)

    newsletter_info = NewsletterInfo(date=today, summary=summary, stories=stories)
    newsletter_info.save()

    if event.push_to_bucket:
        bucket_name = f"inews-{event.stage._value_}"
        io.push_newsletters_to_bucket(bucket_name)

    print("Building all newsletter versions")
    newsletters = []
    for group_id, _ in enumerate(mailing_config["mc_group_interest_values"]):
        read_time = newsletter_info.read_times[group_id]
        newsletter = Newsletter(info=newsletter_info, group_id=group_id, read_time=read_time)
        newsletter.build_html()
        newsletter.save_html_build()
        newsletters.append(newsletter)

    return newsletters


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

from pprint import pprint

from mailchimp_marketing.api_client import ApiClientError

from inews.infra import apis, io
from inews.infra.types import NewsletterP, StoryP, UserGroup

mailchimp_api, members_list_id, campaign_id = apis.get_mailchimp()


def get_mailing_list():
    try:
        response = mailchimp_api.lists.get_list_members_info(members_list_id, count=1000)
    except ApiClientError as error:
        print(error)

    for member in response["members"]:
        pprint(member["email_address"])
        pprint(member["merge_fields"])


def get_template():
    try:
        response = mailchimp_api.campaigns.get_content(campaign_id)
    except ApiClientError as error:
        print(error)

    pprint(response["html"])


def build_summary_block(summary: str):
    newsletter_summary_block = io.read_html_template("newsletter_summary_block")
    return newsletter_summary_block.replace("[INEWS:NEWSLETTER_SUMMARY]", summary)


def build_story_block(group_id: UserGroup, story: StoryP, aligned: str = "left"):
    title_block = io.read_html_template(f"{aligned}_aligned_title_block")
    short_story_block = io.read_html_template("short_story_block")
    user_story_block = io.read_html_template("user_story_block")
    story_block = (
        title_block.replace("[INEWS:VIDEO_ID]", story.video_info.id)
        .replace("[INEWS:VIDEO_TITLE]", story.video_info.title)
        .replace("[INEWS:VIDEO_THUMBNAIL_URL]", story.video_info.thumbnail_url)
        .replace("[INEWS:TITLE_STORY]", story.title)
    )
    story_block += short_story_block.replace("[INEWS:SHORT_STORY]", story.short)
    story_block += user_story_block.replace(
        "[INEWS:USER_STORY]", story.user_stories[group_id].user_story
    )
    return story_block


def build_spacer_block():
    return io.read_html_template("spacer_block")


def build_divider_block():
    return io.read_html_template("divider_block")


def create_newsletter(newsletter: NewsletterP):
    content = ""
    content += build_summary_block(newsletter.summary)
    content += build_spacer_block()

    for idx, story in enumerate(newsletter.stories):
        alignment = "left" if (idx % 2) == 0 else "right"
        content += build_story_block(newsletter.group_id, story, alignment)
        if idx < len(newsletter.stories) - 1:
            content += build_divider_block()

    newsletter_template = io.read_html_template("newsletter")
    newsletter = newsletter_template.replace("[INEWS:CONTENT_PLACEHOLDER]", content)
    return newsletter

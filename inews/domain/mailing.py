from pprint import pprint

from mailchimp_marketing.api_client import ApiClientError

from inews.infra import apis, io
from inews.infra.models import Summary, UserGroup

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


def build_story_block(user_group: UserGroup, summary: Summary, aligned: str = "left"):
    newsletter_summary_block = io.read_html_template(f"{aligned}_aligned_block")
    user_summary_block = io.read_html_template("user_summary_block")
    story_block = (
        newsletter_summary_block.replace("[INEWS:VIDEO_ID]", summary.infos.video_id)
        .replace("[INEWS:VIDEO_TITLE]", summary.infos.video_title)
        .replace("[INEWS:VIDEO_THUMBNAIL_URL]", summary.infos.thumbnail_url)
        .replace("[INEWS:TITLE_SUMMARY]", summary.title)
        .replace("[INEWS:SHORT_SUMMARY]", summary.short)
    )
    story_block += user_summary_block.replace(
        "[INEWS:USER_SUMMARY]", summary.user_groups[user_group].summary
    )
    return story_block


def build_spacer_block():
    return io.read_html_template("spacer_block")


def build_divider_block():
    return io.read_html_template("divider_block")


def create_newsletter(user: UserGroup, summaries: list[Summary]):
    content = ""
    newsletter_summary = "This is the newsletter summary."
    content += build_summary_block(
        f"Here's a recap of what we have for you this week:\n{newsletter_summary}"
    )
    content += build_spacer_block()

    for idx, summary in enumerate(summaries):
        alignment = "left" if (idx % 2) == 0 else "right"
        content += build_story_block(user, summary, alignment)
        if idx < len(summaries) - 1:
            content += build_divider_block()

    newsletter_template = io.read_html_template("newsletter")
    newsletter = newsletter_template.replace("[INEWS:CONTENT_PLACEHOLDER]", content)
    io.write_html(newsletter, f"newsletter_testing_{user}")

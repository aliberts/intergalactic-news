from inews.infra import io
from inews.infra.types import NewsletterP, StoryP, UserGroup


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
    content += build_summary_block(newsletter.info.summary)
    content += build_spacer_block()

    for idx, story in enumerate(newsletter.info.stories):
        alignment = "left" if (idx % 2) == 0 else "right"
        content += build_story_block(newsletter.group_id, story, alignment)
        if idx < len(newsletter.info.stories) - 1:
            content += build_divider_block()

    newsletter_template = io.read_html_template("newsletter")
    newsletter = newsletter_template.replace("[INEWS:CONTENT_PLACEHOLDER]", content)
    return newsletter
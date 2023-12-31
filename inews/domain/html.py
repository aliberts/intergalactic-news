import pendulum

from inews.infra import io
from inews.infra.types import NewsletterP, StoryP, UserGroup


def build_summary_block(summary: str, read_time: int):
    newsletter_summary_block = io.load_html_template("newsletter_summary_block")
    read_time_display = pendulum.duration(seconds=read_time)
    display_text = f"{summary}\n ({read_time_display.minutes} min read)"
    return newsletter_summary_block.replace("[INEWS:NEWSLETTER_SUMMARY]", display_text)


def build_story_block(group_id: UserGroup, story: StoryP, aligned: str = "left"):
    title_block = io.load_html_template(f"{aligned}_aligned_title_block")
    short_story_block = io.load_html_template("short_story_block")
    user_story_block = io.load_html_template("user_story_block")
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
    story_block += build_content_credits_block(story)
    return story_block


def build_content_credits_block(story: StoryP):
    user_story_block = io.load_html_template("user_story_block")
    story_credit = f"Credits: {story.channel_info.name}"
    return user_story_block.replace("[INEWS:USER_STORY]", story_credit)


def build_spacer_block():
    return io.load_html_template("spacer_block")


def build_divider_block():
    return io.load_html_template("divider_block")


def build_large_divider_block():
    return io.load_html_template("large_divider_block")


def build_credits_block():
    return io.load_html_template("credits_block")


def create_newsletter(newsletter: NewsletterP):
    content = ""
    content += build_summary_block(newsletter.info.summary, newsletter.read_time)
    content += build_spacer_block()

    for idx, story in enumerate(newsletter.info.stories):
        alignment = "left" if (idx % 2) == 0 else "right"
        content += build_story_block(newsletter.group_id, story, alignment)
        if idx < len(newsletter.info.stories) - 1:
            content += build_divider_block()

    content += build_large_divider_block()
    content += build_credits_block()

    newsletter_template = io.load_html_template("newsletter")
    newsletter = newsletter_template.replace("[INEWS:CONTENT_PLACEHOLDER]", content)
    return newsletter

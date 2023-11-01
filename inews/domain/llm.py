from inews.domain import preprocessing, prompts
from inews.infra import apis
from inews.infra.types import SummaryP, UserGroup, VideoP

openai_api = apis.get_openai()

WINDOW_THRESHOLD = 3500
TEMPERATURE = 0.4

DEBUG = False


def generate_base_summary_prompt(summary: SummaryP, video: VideoP) -> str:
    return prompts.BASE_SUMMARY.format(
        video_title=summary.video_infos.title,
        channel_name=summary.channel_infos.name,
        transcript=video.transcript.text,
    )


def generate_short_summary_prompt(summary: SummaryP) -> str:
    return prompts.SHORT_SUMMARY.format(
        video_title=summary.video_infos.title,
        channel_name=summary.channel_infos.name,
        summary=summary.base,
    )


def generate_title_summary_prompt(summary: SummaryP) -> str:
    return prompts.TITLE_SUMMARY.format(
        video_title=summary.video_infos.title,
        channel_name=summary.channel_infos.name,
        summary=summary.base,
    )


def generate_user_summary_prompt(summary: SummaryP, user_group: UserGroup) -> str:
    return prompts.USER_SUMMARY.format(
        user_science_cat=prompts.SCIENCE_GROUP_TO_PROMPT[user_group],
        video_title=summary.video_infos.title,
        channel_name=summary.channel_infos.name,
        summary=summary.base,
    )


def generate_stories_selection_prompt(summaries: list[SummaryP]) -> str:
    titles_and_shorts = ""
    for idx, summary in enumerate(summaries):
        titles_and_shorts += f"\n{str(idx + 1)}. {summary.title}\n{summary.short}\n"
    return prompts.STORIES_SELECTION.format(titles_and_shorts=titles_and_shorts)


def generate_newsletter_summary_prompt(*args, **kwargs) -> str:
    ...


def get_model_response(prompt: str) -> str:
    if DEBUG:
        return "This is a model response"
    tokens_count = preprocessing.count_tokens(prompt)
    model = "gpt-3.5-turbo" if tokens_count < WINDOW_THRESHOLD else "gpt-3.5-turbo-16k"
    print(f"tokens: {tokens_count}, using {model}")
    completion = openai_api.ChatCompletion.create(
        model=model,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


def get_base_summary(summary: SummaryP, video: VideoP) -> str:
    if DEBUG:
        return "This is a base summary"
    prompt = generate_base_summary_prompt(summary, video)
    return get_model_response(prompt)


def get_short_summary(summary: SummaryP) -> str:
    if DEBUG:
        return "This is a short summary"
    prompt = generate_short_summary_prompt(summary)
    return get_model_response(prompt)


def get_title_summary(summary: SummaryP) -> str:
    if DEBUG:
        return "This is a title"
    prompt = generate_title_summary_prompt(summary)
    return get_model_response(prompt)


def get_user_summary(summary: SummaryP, user_group: UserGroup) -> str:
    if DEBUG:
        return (
            f"This is a summary for a user with {prompts.SCIENCE_GROUP_TO_PROMPT[user_group]}"
            + "-level scientific background"
        )
    prompt = generate_user_summary_prompt(summary, user_group)
    return get_model_response(prompt)


def get_stories_selection(summaries: list[SummaryP]) -> str:
    prompt = generate_stories_selection_prompt(summaries)
    return get_model_response(prompt)


def get_newsletter_summary(*args, **kwargs) -> str:
    ...

from inews.domain import preprocessing, prompts
from inews.infra import apis
from inews.infra.types import UserGroup

openai_api = apis.get_openai()

WINDOW_THRESHOLD = 3500
TEMPERATURE = 0.4

DEBUG = True


def generate_base_summary_prompt(video_title: str, channel_name: str, transcript: str) -> str:
    return prompts.BASE_SUMMARY.format(
        video_title=video_title,
        channel_name=channel_name,
        transcript=transcript,
    )


def generate_short_summary_prompt(video_title: str, channel_name: str, base_summary: str) -> str:
    return prompts.SHORT_SUMMARY.format(
        video_title=video_title,
        channel_name=channel_name,
        summary=base_summary,
    )


def generate_title_summary_prompt(video_title: str, channel_name: str, base_summary: str) -> str:
    return prompts.TITLE_SUMMARY.format(
        video_title=video_title,
        channel_name=channel_name,
        summary=base_summary,
    )


def generate_user_summary_prompt(
    video_title: str, channel_name: str, base_summary: str, user_group: UserGroup
) -> str:
    return prompts.USER_SUMMARY.format(
        user_science_cat=prompts.SCIENCE_GROUP_TO_PROMPT[user_group],
        video_title=video_title,
        channel_name=channel_name,
        summary=base_summary,
    )


def generate_stories_selection_prompt(*args, **kwargs) -> str:
    ...


def generate_newsletter_summary_prompt(*args, **kwargs) -> str:
    ...


def get_model_response(prompt: str) -> str:
    if DEBUG:
        return "This is a model response"
    tokens_count = preprocessing.count_tokens(prompt)
    model = "gpt-3.5-turbo-16k" if tokens_count > WINDOW_THRESHOLD else "gpt-3.5-turbo"
    completion = openai_api.ChatCompletion.create(
        model=model,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


def get_base_summary(video_title: str, channel_name: str, transcript: str) -> str:
    if DEBUG:
        return "This is a base summary"
    prompt = generate_base_summary_prompt(video_title, channel_name, transcript)
    return get_model_response(prompt)


def get_short_summary(video_title: str, channel_name: str, base_summary: str) -> str:
    if DEBUG:
        return "This is a short summary"
    prompt = generate_short_summary_prompt(video_title, channel_name, base_summary)
    return get_model_response(prompt)


def get_title_summary(video_title: str, channel_name: str, base_summary: str) -> str:
    if DEBUG:
        return "This is a title"
    prompt = generate_title_summary_prompt(video_title, channel_name, base_summary)
    return get_model_response(prompt)


def get_user_summary(
    video_title: str, channel_name: str, base_summary: str, user_group: UserGroup
) -> str:
    if DEBUG:
        return (
            f"This is a summary for a user with {prompts.SCIENCE_GROUP_TO_PROMPT[user_group]}"
            + "-level scientific background"
        )
    prompt = generate_user_summary_prompt(video_title, channel_name, base_summary, user_group)
    return get_model_response(prompt)


def get_stories_selection(*args, **kwargs) -> str:
    ...


def get_newsletter_summary(*args, **kwargs) -> str:
    ...

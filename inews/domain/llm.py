from inews.domain import preprocessing, prompts
from inews.infra import apis
from inews.infra.types import UserGroup

openai_api = apis.get_openai()

WINDOW_THRESHOLD = 3500
TEMPERATURE = 0.4


def generate_base_prompt(video_title: str, channel_name: str, transcript: str) -> str:
    return prompts.BASE_SUMMARY.format(
        video_title=video_title,
        channel_name=channel_name,
        transcript=transcript,
    )


def generate_user_prompt(
    video_title: str, channel_name: str, base_summary: str, user_group: UserGroup
) -> str:
    return prompts.USER_SUMMARY.format(
        user_science_cat=prompts.SCIENCE_GROUP_TO_PROMPT[user_group],
        video_title=video_title,
        channel_name=channel_name,
        summary=base_summary,
    )


def get_model_response(prompt: str) -> str:
    return ""
    return prompts.BASE_SUMMARY_EXAMPLE
    tokens_count = preprocessing.count_tokens(prompt)
    model = "gpt-3.5-turbo-16k" if tokens_count > WINDOW_THRESHOLD else "gpt-3.5-turbo"
    completion = openai_api.ChatCompletion.create(
        model=model,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


def get_base_summary(video_title: str, channel_name: str, transcript: str) -> str:
    prompt = generate_base_prompt(video_title, channel_name, transcript)
    return get_model_response(prompt)


def get_short_summary(video_title: str, channel_name: str, base_summary: str) -> str:
    return ""


def get_title(video_title: str, channel_name: str, base_summary: str) -> str:
    return ""


def get_user_summary(
    video_title: str, channel_name: str, base_summary: str, user_group: UserGroup
) -> str:
    prompt = generate_user_prompt(video_title, channel_name, base_summary, user_group)
    return get_model_response(prompt)

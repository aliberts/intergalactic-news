from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm

from inews.domain import preprocessing, prompts
from inews.infra import apis, io
from inews.infra.types import StoryP, SummaryP, UserGroup, VideoP

data_config = io.get_data_config()
openai_api = apis.get_openai()

WINDOW_THRESHOLD = 3500
TEMPERATURE = 0.7

DEBUG = False


def generate_base_summary_prompt(summary: SummaryP, video: VideoP) -> str:
    return prompts.BASE_SUMMARY.format(
        video_title=summary.video_info.title,
        channel_name=summary.channel_info.name,
        transcript=video.transcript.text,
    )


def generate_topics_prompt(summary: SummaryP) -> str:
    return prompts.TOPICS.format(
        number_of_topics=data_config["number_of_topics"],
        video_title=summary.video_info.title,
        channel_name=summary.channel_info.name,
        summary=summary.base,
    )


def generate_short_story_prompt(summary: SummaryP) -> str:
    return prompts.SHORT_STORY.format(
        video_title=summary.video_info.title,
        channel_name=summary.channel_info.name,
        summary=summary.base,
    )


def generate_title_story_prompt(summary: SummaryP) -> str:
    return prompts.TITLE_STORY.format(
        video_title=summary.video_info.title,
        channel_name=summary.channel_info.name,
        summary=summary.base,
    )


def generate_user_story_prompt(summary: SummaryP, user_group: UserGroup) -> str:
    return prompts.USER_STORY.format(
        user_science_cat=prompts.GROUP_TO_PROMPT[user_group],
        video_title=summary.video_info.title,
        channel_name=summary.channel_info.name,
        summary=summary.base,
    )


def generate_stories_selection_from_topics_prompt(summaries: list[SummaryP]) -> str:
    topics = ""
    for idx, summary in enumerate(summaries):
        topics += f"\n{str(idx + 1)}. {summary.topics}\n"
    return prompts.STORIES_SELECTION_FROM_TOPICS.format(topics=topics)


def generate_newsletter_summary_prompt(stories: list[StoryP]) -> str:
    titles_and_shorts = ""
    for idx, story in enumerate(stories):
        titles_and_shorts += f"\n{str(idx + 1)}. {story.title}\n{story.short}\n"
    return prompts.NEWSLETTER_SUMMARY.format(titles_and_shorts=titles_and_shorts)


@retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(5))
def chat_completion(model: str, temperature: float, messages: list[dict]) -> dict:
    return openai_api.ChatCompletion.create(
        model=model,
        temperature=temperature,
        messages=messages,
    )


def get_model_response(prompt: str) -> str:
    if DEBUG:
        return "This is a model response"
    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    messages_tokens_count = preprocessing.count_tokens_from_messages(messages)
    model = "gpt-3.5-turbo" if messages_tokens_count < WINDOW_THRESHOLD else "gpt-3.5-turbo-16k"
    tqdm.write(f"tokens: {messages_tokens_count}, using {model}")

    completion = chat_completion(
        model=model,
        temperature=TEMPERATURE,
        messages=messages,
    )

    return completion.choices[0].message.content


def get_base_summary(summary: SummaryP, video: VideoP) -> str:
    if DEBUG:
        return "This is a base summary"
    prompt = generate_base_summary_prompt(summary, video)
    return get_model_response(prompt)


def get_topics(summary: SummaryP) -> str:
    if DEBUG:
        return "This is a list of topics"
    prompt = generate_topics_prompt(summary)
    return get_model_response(prompt)


def get_stories_selection_from_topics(summaries: list[SummaryP]) -> list[str]:
    if DEBUG:
        return ["no", "yes", "no", "yes"]
    prompt = generate_stories_selection_from_topics_prompt(summaries)
    return get_model_response(prompt).lower().split(",")


def get_short_summary(summary: SummaryP) -> str:
    if DEBUG:
        return "This is a short story"
    prompt = generate_short_story_prompt(summary)
    return get_model_response(prompt)


def get_title_summary(summary: SummaryP) -> str:
    if DEBUG:
        return "This is a title story"
    prompt = generate_title_story_prompt(summary)
    return get_model_response(prompt)


def get_user_story(summary: SummaryP, user_group: UserGroup) -> str:
    if DEBUG:
        return (
            f"This is a user story for a user with {prompts.GROUP_TO_PROMPT[user_group]}"
            + "-level scientific background"
        )
    prompt = generate_user_story_prompt(summary, user_group)
    return get_model_response(prompt)


def get_newsletter_summary(stories: list[StoryP]) -> str:
    if DEBUG:
        return "This is a newsletter summary"
    prompt = generate_newsletter_summary_prompt(stories)
    return get_model_response(prompt)

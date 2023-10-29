from inews.domain import preprocessing, prompts
from inews.infra import apis
from inews.infra.models import BaseSummary, Summary, SummaryInfo, Transcript, UserBase, UserSummary

openai_api = apis.get_openai()

WINDOW_THRESHOLD = 3500
TEMPERATURE = 0.4


def generate_base_prompt(transcript: Transcript) -> str:
    return prompts.BASE_SUMMARY.format(
        video_title=transcript.video_title,
        channel_name=transcript.channel_name,
        transcript=transcript.transcript,
    )


def generate_user_prompt(summary: Summary, user: UserBase) -> str:
    return prompts.USER_SUMMARY.format(
        user_science_cat=prompts.SCIENCE_CAT_TO_PROMPT[user.science_cat],
        video_title=summary.infos.video_title,
        channel_name=summary.infos.channel_name,
        summary=summary.base_summary.summary,
    )


def get_model_response(prompt: str) -> str:
    return prompts.BASE_SUMMARY_EXAMPLE
    tokens_count = preprocessing.count_tokens(prompt)
    model = "gpt-3.5-turbo-16k" if tokens_count > WINDOW_THRESHOLD else "gpt-3.5-turbo"
    completion = openai_api.ChatCompletion.create(
        model=model,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


def get_base_summary(transcript: Transcript) -> BaseSummary:
    prompt = generate_base_prompt(transcript)
    base_summary = get_model_response(prompt)
    tokens_count = preprocessing.count_tokens(base_summary)
    return BaseSummary(tokens_count=tokens_count, summary=base_summary)


def get_user_summary(summary: Summary, user: UserBase) -> UserSummary:
    prompt = generate_user_prompt(summary, user)
    user_summary = get_model_response(prompt)
    return UserSummary(user=user, summary=user_summary)


def get_summary_info(transcript: Transcript) -> SummaryInfo:
    return SummaryInfo(
        **{
            "channel_id": transcript.channel_id,
            "channel_name": transcript.channel_name,
            "video_id": transcript.video_id,
            "video_title": transcript.video_title,
            "date": transcript.date,
            "duration": transcript.duration,
            "thumbnail_url": transcript.thumbnail_url,
            "from_generated": transcript.is_generated,
        }
    )

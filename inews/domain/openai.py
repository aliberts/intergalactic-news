from inews.domain import preprocessing, prompts
from inews.infra import apis, io
from inews.infra.models import (
    BaseSummary,
    Summary,
    SummaryInfo,
    Transcript,
    TranscriptList,
    User,
    UserSummary,
)

openai_api = apis.get_openai()
TEMPERATURE = 0.4
WINDOW_THRESHOLD = 3500


def generate_base_prompt(transcript: Transcript) -> str:
    return prompts.BASE_SUMMARY.format(
        video_title=transcript.video_title,
        channel_name=transcript.channel_name,
        transcript=transcript.transcript,
    )


def generate_user_prompt(summary: Summary, user: User) -> str:
    return prompts.USER_SUMMARY.format(
        user_age=prompts.AGE_CAT_TO_PROMPT[user.age_cat],
        user_science_cat=prompts.SCIENCE_CAT_TO_PROMPT[user.science_cat],
        video_title=summary.infos.video_title,
        channel_name=summary.infos.channel_name,
        summary=summary.base_summary.summary,
    )


def get_model_response(prompt: str) -> str:
    # return prompts.BASE_SUMMARY_EXAMPLE
    tokens_count = preprocessing.count_tokens(prompt)
    if tokens_count > WINDOW_THRESHOLD:
        model = "gpt-3.5-turbo-16k"
    else:
        model = "gpt-3.5-turbo"

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


def get_user_summary(summary: Summary, user: User) -> UserSummary:
    prompt = generate_user_prompt(summary, user)
    user_summary = get_model_response(prompt)
    return UserSummary(user=user, summary=user_summary)


def get_summary_info(transcript: Transcript) -> SummaryInfo:
    return SummaryInfo(
        **{
            "video_id": transcript.video_id,
            "video_title": transcript.video_title,
            "channel_id": transcript.channel_id,
            "channel_name": transcript.channel_name,
            "date": transcript.date,
            "from_generated": transcript.is_generated,
        }
    )


def build_summaries(transcripts_list: TranscriptList) -> dict[str:BaseSummary]:
    users = [User(age_cat=2, science_cat=0), User(age_cat=0, science_cat=2)]
    for transcript in transcripts_list:
        summary_info = get_summary_info(transcript)
        base_summary = get_base_summary(transcript)
        summary = Summary(
            infos=summary_info,
            base_summary=base_summary,
            user_summaries=[],
        )
        io.write_summary(summary)  # checkpoint to save base summaries first)
        for user in users:
            user_summary = get_user_summary(summary, user)
            summary.user_summaries.append(user_summary)
        io.write_summary(summary)

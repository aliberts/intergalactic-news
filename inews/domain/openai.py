from inews.domain import preprocessing, prompts
from inews.infra import apis, io
from inews.infra.models import (
    BaseSummary,
    BaseSummaryList,
    Transcript,
    TranscriptList,
    User,
    UserSummary,
)

openai_api = apis.get_openai()
TEMPERATURE = 0.4


def generate_base_prompt(transcript: Transcript) -> str:
    return prompts.BASE_SUMMARY.format(
        video_title=transcript.video_title,
        channel_name=transcript.channel_name,
        transcript=transcript.transcript,
    )


def generate_user_prompt(summary: BaseSummary, user: User) -> str:
    return prompts.USER_SUMMARY.format(
        user_age=user.age_bin,
        user_science_level=user.science_level,
        video_title=summary.video_title,
        channel_name=summary.channel_name,
        summary=summary.summary,
    )


def get_model_response(prompt: str) -> str:
    completion = openai_api.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


def get_base_summary(transcript: Transcript) -> str:
    prompt = generate_base_prompt(transcript)
    return get_model_response(prompt)


def get_base_summaries(
    transcripts_list: TranscriptList,
) -> BaseSummaryList:
    summary_list = []
    for transcript in transcripts_list:
        summary = get_base_summary(transcript)
        tokens_count = preprocessing.count_tokens(summary)
        summary_list.append(
            {
                "video_id": transcript.video_id,
                "video_title": transcript.video_title,
                "channel_id": transcript.channel_id,
                "channel_name": transcript.channel_name,
                "date": transcript.date,
                "from_generated": transcript.is_generated,
                "tokens_count": tokens_count,
                "summary": summary,
            }
        )
    summary_list = BaseSummaryList.model_validate(summary_list)
    io.write_base_summaries(summary_list)
    return summary_list


def get_user_summary(summary: BaseSummary, user: User) -> UserSummary:
    prompt = generate_user_prompt(summary, user)
    return get_model_response(prompt)


def get_user_summaries(base_summary_list: BaseSummaryList, user: User) -> UserSummary:
    user_summary_list = []
    for base_summary in base_summary_list:
        user_summary = get_user_summary(base_summary, user)
        tokens_count = preprocessing.count_tokens(user_summary)
        user_summary_list.append(
            {
                "video_id": base_summary.video_id,
                "video_title": base_summary.video_title,
                "channel_id": base_summary.channel_id,
                "channel_name": base_summary.channel_name,
                "date": base_summary.date,
                "from_generated": base_summary.from_generated,
                "tokens_count": tokens_count,
                "summary": user_summary,
            }
        )
    user_summary = UserSummary(user=user, summaries=user_summary_list)
    io.write_user_summaries(user_summary)
    return user_summary

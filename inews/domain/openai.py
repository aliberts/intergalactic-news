from inews.domain import preprocessing, prompts
from inews.infra import apis
from inews.infra.models import (
    BaseSummary,
    BaseSummaryList,
    User,
    UserSummary,
    YoutubeVideoTranscript,
    YoutubeVideoTranscriptList,
)

openai_api = apis.get_openai()
TEMPERATURE = 0.4


def generate_base_prompt(transcript: YoutubeVideoTranscript) -> str:
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
    # return prompts.SUMMARY
    return completion.choices[0].message.content


def get_base_summary(transcript: YoutubeVideoTranscript) -> str:
    prompt = generate_base_prompt(transcript)
    return get_model_response(prompt)


def get_base_summaries(
    transcripts_obj_list: YoutubeVideoTranscriptList,
) -> BaseSummaryList:
    summary_obj_list = []
    for transcript in transcripts_obj_list.transcripts:
        summary = get_base_summary(transcript)
        tokens_count = preprocessing.count_tokens(summary)
        summary_obj_list.append(
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
    return BaseSummaryList(transcripts=summary_obj_list)


def get_user_summary(summary: BaseSummary, user: User) -> UserSummary:
    prompt = generate_user_prompt(summary, user)
    return get_model_response(prompt)


def get_user_summaries(summary_obj_list: BaseSummaryList, user: User) -> UserSummary:
    summary_obj_list = []
    for summary in summary_obj_list.summaries:
        summary = get_user_summary(summary, user)
        tokens_count = preprocessing.count_tokens(summary)
        summary_obj_list.append(
            {
                "video_id": summary.video_id,
                "video_title": summary.video_title,
                "channel_id": summary.channel_id,
                "channel_name": summary.channel_name,
                "date": summary.date,
                "from_generated": summary.is_generated,
                "tokens_count": tokens_count,
                "summary": summary,
            }
        )
    return UserSummary(user=user, summaries=summary_obj_list)

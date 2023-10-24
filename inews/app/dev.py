from pathlib import Path
from statistics import mean

from inews.domain import preprocessing
from inews.infra import io

PROMPTS_DATA_PATH = Path("data/prompts/")

PROMPT1_TEMPLATE = """The following is the transcript of a youtube video by
youtube channel {channel_name}. This is a channel that talks
mainly about astronomy and astrophysics and relevant news in
these fields. The title of the video is "{video_title}".

Write a short summary (3-4 paragraphs) of this transcript,
intended to be read and understood by {user_age} with
{user_science_level}-level scientific background. The
language should be neutral and tailored for this specific
audience. At the end, explain how the topic of the video is
relevant to someone having an interest in astrophysics,
astronomy or astronautics.

Transcript:
{transcript}"""


PROMPT2_TEMPLATE = """As a professional summarizer, create a concise and
comprehensive summary of the provided text, while adhering
to these guidelines:

Craft a summary that is detailed, thorough, in-depth, and
complex, while maintaining clarity and conciseness.

Incorporate main ideas and essential information,
eliminating extraneous language and focusing on critical
aspects.

Rely strictly on the provided text, without including
external information.

Format the summary in paragraph form for easy understanding.

Conclude your notes with [End of Notes, Message #X] to
indicate completion, where "X" represents the total number
of messages that I have sent. In other words, include a
message counter where you start with #1 and add 1 to the
message counter every time I send a message.

The provided text is the transcript of a Youtube video
titled "{video_title}" produced by Youtube channel
{channel_name}.

Transcript:
{transcript}"""

USER_AGE_CHOICE = [
    "a 6 years-old child",
    "a 14 years-old teenager",
    "an adult",
]

USER_SCIENCE_LEVEL_CHOICE = [
    "a beginner",
    "an average",
    "an expert",
]


def generate_prompts():
    transcript_list = io.read_transcripts()
    for idx, transcript in enumerate(transcript_list):
        if transcript.tokens_count < 500:
            transcript_list.pop(idx)

    for transcript in transcript_list:
        prompt1 = PROMPT1_TEMPLATE.format(
            user_age=USER_AGE_CHOICE[2],
            user_science_level=USER_SCIENCE_LEVEL_CHOICE[2],
            video_title=transcript.video_title,
            channel_name=transcript.channel_name,
            transcript=transcript.transcript,
        )
        prompt2 = PROMPT2_TEMPLATE.format(
            video_title=transcript.video_title,
            channel_name=transcript.channel_name,
            transcript=transcript.transcript,
        )
        pth = PROMPTS_DATA_PATH / f"{transcript.video_id}__{transcript.tokens_count}"
        pth.mkdir(exist_ok=True)
        file_path1 = pth / "prompt1.txt"
        file_path2 = pth / "prompt2.txt"
        with open(file_path1, "w") as file1, open(file_path2, "w") as file2:
            file1.write(prompt1)
            file2.write(prompt2)


def get_transcripts_stats():
    transcript_list = io.read_transcripts()
    for idx, transcript in enumerate(transcript_list):
        if transcript.tokens_count < 500:
            transcript_list.pop(idx)

    prompt1_count_list = []

    for transcript in transcript_list:
        prompt1 = PROMPT1_TEMPLATE.format(
            user_age=USER_AGE_CHOICE[2],
            user_science_level=USER_SCIENCE_LEVEL_CHOICE[2],
            video_title=transcript.video_title,
            channel_name=transcript.channel_name,
            transcript=transcript.transcript,
        )
        prompt1_count_list.append(preprocessing.count_tokens(prompt1))

    print(prompt1_count_list)
    print(mean(prompt1_count_list))


if __name__ == "__main__":
    # generate_prompts()
    get_transcripts_stats()

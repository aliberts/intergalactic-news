from pathlib import Path
from statistics import mean

from inews.domain import openai, preprocessing
from inews.infra import io

PROMPTS_DATA_PATH = Path("data/prompts/")

PROMPT1_TEMPLATE = """The following is the transcript of a
youtube video by youtube channel {channel_name}. This is a channel that talks
mainly about astronomy and astrophysics and relevant news in these fields.

The title of the video is "{video_title}".

Write a short summary (3-4 paragraphs) of this transcript, intended to be read
and understood by {user_age} with {user_science_cat}-level scientific
background. The language should be neutral and tailored for this specific
audience. At the end, explain how the topic of the video is relevant to someone
having an interest in astrophysics, astronomy or astronautics.

Transcript: {transcript}"""


PROMPT2_TEMPLATE = """As a professional summarizer, create
a concise and comprehensive summary of the provided text, while adhering to
these guidelines:

Craft a summary that is detailed, thorough, in-depth, and complex, while
maintaining clarity and conciseness.

Incorporate main ideas and essential information, eliminating extraneous
language and focusing on critical aspects.

Rely strictly on the provided text, without including external information.

Format the summary in paragraph form for easy understanding.

Conclude your notes with [End of Notes, Message #X] to indicate completion,
where "X" represents the total number of messages that I have sent. In other
words, include a message counter where you start with #1 and add 1 to the
message counter every time I send a message.

The provided text is the transcript of a Youtube video titled "{video_title}"
produced by Youtube channel {channel_name}.

Transcript: {transcript}"""

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


SUMMARY = """
The Gaia Space Telescope, known for its detailed mapping of the sky, recently
released a new set of data called the focused product release (FPR), which
contains information on approximately 1.8 billion stars as well as other objects
in the solar system. One of the notable discoveries from this data release is
the identification of half a million new stars in a well-known globular cluster
called Omega Centauri. These stars were previously difficult to study due to
their close proximity to one another, but the new data allows scientists to
study their movements and interactions. Additionally, the Gaia telescope
accidentally discovered gravitational lenses, indicating the presence of distant
quasars. A total of 381 candidates, with 50 confirmed as new quasars, were
found, including five rare quadruple lens quasars. The release also revealed
approximately 10,000 variable stars, which are useful for measuring distances to
various objects in the universe. Furthermore, the FPR data included information
on 150,000 asteroids, allowing for more precise calculations of their orbits and
potential impact risks to Earth.

In a separate release, the SiGN Galaxy Atlas, compiled by scientists from the
National Science Foundation using NOIRLab telescopes, contains 400,000 galaxies
in our cosmic neighborhood. This survey, which captured images in both optical
and infrared light, represents the largest galactic survey to date and provides
the most detailed map of the night sky. The data includes recalculated
measurements such as red shift distance, improving the accuracy of previous
surveys. The atlas is freely accessible online, allowing anyone, including
amateur astronomers, to explore the galaxies and use the data for their own
studies.

These releases demonstrate the significant advancements in astronomy and the
accessibility of data in recent years. They provide valuable insights into the
movements and origins of stars, the presence of quasars and gravitational
lenses, and the formation and evolution of galaxies. The data will be
instrumental in future studies of the universe and will help scientists unravel
the mysteries of dark matter, dark energy, and the nature of the Milky Way.
Overall, these discoveries highlight the importance of missions like Gaia and
the collaborative efforts of organizations like Isa and NOIRLab in expanding our
understanding of the universe.
"""


def generate_prompts():
    transcript_list = io.read_available_transcripts()
    for idx, transcript in enumerate(transcript_list):
        if transcript.tokens_count < 500:
            transcript_list.pop(idx)

    for transcript in transcript_list:
        prompt1 = PROMPT1_TEMPLATE.format(
            user_age=USER_AGE_CHOICE[2],
            user_science_cat=USER_SCIENCE_LEVEL_CHOICE[2],
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
    transcript_list = io.read_available_transcripts()
    for idx, transcript in enumerate(transcript_list):
        if transcript.tokens_count < 500:
            transcript_list.pop(idx)

    prompt1_count_list = []

    for transcript in transcript_list:
        prompt1 = PROMPT1_TEMPLATE.format(
            user_age=USER_AGE_CHOICE[2],
            user_science_cat=USER_SCIENCE_LEVEL_CHOICE[2],
            video_title=transcript.video_title,
            channel_name=transcript.channel_name,
            transcript=transcript.transcript,
        )
        prompt1_count_list.append(preprocessing.count_tokens(prompt1))

    print(prompt1_count_list)
    print(f"average tokens count: {mean(prompt1_count_list):.1f}")


def test_openai_api():
    prompt = "Write 'hello world!'"
    response = openai.get_model_response(prompt)
    print(response)


if __name__ == "__main__":
    generate_prompts()
    get_transcripts_stats()

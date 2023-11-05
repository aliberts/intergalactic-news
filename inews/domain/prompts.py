import pendulum

SYSTEM_PROMPT = f"""You are ChatGPT, a large language model
trained by OpenAI, based on the GPT-3.5 architecture.
Knowledge cutoff: 2021-09
Current date: {pendulum.now().date()}"""


GROUP_TO_PROMPT = [
    "a beginner",
    "an average",
    "an expert",
]


BASE_SUMMARY = """You will be given the transcript of a youtube video titled
"{video_title}" by youtube channel {channel_name}.

Write an exhaustive summary of this video that is detailed, thorough, in-depth
and complex, while maintaining clarity and conciseness. Incorporate main ideas
and essential information, eliminating extraneous language and focusing on
critical aspects. Rely strictly on the provided text, without including external
information.

Transcript:
{transcript}

Your detailled summary:"""


TOPICS = """You will be given the transcript of a youtube video titled
"{video_title}" by youtube channel {channel_name}.

Write {number_of_topics} words describing the general topic of the video.

You will give your answer in the form of a comma-separated list with only the 3
words you chose and nothing else. THIS IS VERY IMPORTANT.

For example, if a video talks about the lastest iPhone release, your answer
should be: Technology, Apple, iPhone

Summarized transcript:
{summary}

Your answer:"""


STORIES_SELECTION_FROM_TOPICS = """You will be given a numbered list of words
describing a common topic. The list will look like this:

1. [words about a common topic]

2. [words about a common topic]

...

For each item in this list, your task is to anwser "yes" or "no" to the
following question: Does the topic fall into any of the categories Astronomy,
Astrophysics, Physics or Space Science ?

You will give your answer in the form of a comma-separated list with only "yes"
or "no" values and nothing else. For example, if you are given 10 different
items and you choose to answer "yes" to items number 1, 4, 5 and 9, your answer
should be: "Yes,No,No,Yes,Yes,No,No,No,Yes,No"

List of common topics:
{topics}
Your answer:"""


SHORT_STORY = """You will be given the summarized transcript
of a youtube video titled "{video_title}" by youtube channel {channel_name}.

Your task is to write a very short summary of this video. The length of your
summary should not exceed 3 sentences. The language should be entice the reader
to know more about it while remaining factual. Do not refer to the video and
relate the facts directly.

Summarized transcript:
{summary}

Your short summary:"""


TITLE_STORY = """You will be given the summarized transcript
of a youtube video titled "{video_title}" by youtube channel {channel_name}.

Your task is to write an alternative title to this video that fully conveys the
topic of the video. The language should be neutral, factual and not
clickbaiting. Do not add quotation marks arround your title.

Summarized transcript:
{summary}

Your alternative title:"""


USER_STORY = """You will be given the summarized transcript
of a youtube video titled "{video_title}" by youtube channel {channel_name}.

Your task is to adapt this to a short summary (2-3 paragraphs maximum) of this
transcript, intended to be read and understood by someone with
{user_science_cat}-level scientific background. The language should be neutral
and tailored for this specific audience. Do not refer to the video and relate
the facts directly.

Summarized transcript:
{summary}

Your summary tailored for the given audience:"""


# TODO: testing
USER_STORY_ALL = """You will be given the summarized transcript
of a youtube video titled "{video_title}" by youtube channel {channel_name}.

Your task is to adapt this summary to be understood by 3 different audiences in
terms of scientific background: beginners, intermediates and experts. For each
audience, the language should be neutral and tailored for this specific
audience. At the end of each version of your summary, explain why the topic of
the video is relevant to someone having an interest in astrophysics, astronomy
or astronautics. Whenever you refer to the video in your answer, refer to it as
"this story" instead of "this video".

You will give your answer in the following form:

1. Beginner: [Your beginner-level summary]

2. Intermediate: [Your intermediate-level summary]

3. Expert: [Your expert-leve summary]

Summarized transcript:
{summary}

Your answer:"""


NEWSLETTER_SUMMARY = """You are writing a newsletter about some articles.
You will be given a numbered list of article's title and summary.
The list will look like this:

1. [Title of the article]
[short summary of the article]

2. [Title of the article]
[short summary of the article]

...

Your task is to write the summary of that newsletter that will serve as an
introdution to the rest of the content. Since it's an introduction, it must be
very brief and just provide the reader with a glimpse of what's in the
newsletter.

List of titles and summaries:
{titles_and_shorts}
Your summary:"""

SCIENCE_GROUP_TO_PROMPT = [
    "a beginner",
    "an average",
    "an expert",
]

BASE_SUMMARY = """The following is the transcript of a
youtube video by youtube channel {channel_name}. This is a channel that talks
mainly about astronomy and astrophysics and relevant news in these fields.

The title of the video is "{video_title}".

Write an exhaustive summary of this transcript that is detailed, thorough,
in-depth, and complex, while maintaining clarity and conciseness. Incorporate
main ideas and essential information, eliminating extraneous language and
focusing on critical aspects. Rely strictly on the provided text, without
including external information.

Transcript:
{transcript}"""


USER_SUMMARY = """The following is a summarized transcript
of a youtube video by youtube channel {channel_name}. This is a channel that
talks mainly about astronomy and astrophysics and relevant news in these fields.

The title of the video is "{video_title}".

Adapt this to a short summary (3-4 paragraphs) of this transcript, intended to
be read and understood by someone with {user_science_cat}-level scientific
background. The language should be neutral and tailored for this specific
audience. At the end, explain why the topic of the video is relevant to someone
having an interest in astrophysics, astronomy or astronautics.

Summarized transcript:
{summary}"""


SHORT_SUMMARY = """The following is a summarized transcript
of a youtube video by youtube channel {channel_name}. This is a channel that
talks mainly about astronomy and astrophysics and relevant news in these fields.

The title of the video is "{video_title}".

Write a very short summary of this transcript. The lenght of your summary should
not exceed 3 sentences. The language should be neutral.

Summarized transcript:
{summary}"""


SUMMARY_TITLE = """The following is a summarized transcript
of a youtube video by youtube channel {channel_name}. This is a channel that
talks mainly about astronomy and astrophysics and relevant news in these fields.

The title of the video is "{video_title}".

Write a very short summary of this transcript. The lenght of your summary should
not exceed 3 sentences. The language should be neutral.

Summarized transcript:
{summary}"""


SELECT_MOST_RELEVANT = """You are helping to generate content for a newsletter.
Your will be given a list of youtube videos titles.

Pick {number_of_videos} of them based on the following criterias:
Relevency

You will give you answer

List of titles:
{titles}
"""


BASE_SUMMARY_EXAMPLE = """The Gaia Space Telescope, known for its detailed
mapping of the sky, recently released a new set of data called the focused
product release (FPR), which contains information on approximately 1.8 billion
stars as well as other objects in the solar system. One of the notable
discoveries from this data release is the identification of half a million new
stars in a well-known globular cluster called Omega Centauri. These stars were
previously difficult to study due to their close proximity to one another, but
the new data allows scientists to study their movements and interactions.
Additionally, the Gaia telescope accidentally discovered gravitational lenses,
indicating the presence of distant quasars. A total of 381 candidates, with 50
confirmed as new quasars, were found, including five rare quadruple lens
quasars. The release also revealed approximately 10,000 variable stars, which
are useful for measuring distances to various objects in the universe.
Furthermore, the FPR data included information on 150,000 asteroids, allowing
for more precise calculations of their orbits and potential impact risks to
Earth.

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
understanding of the universe."""

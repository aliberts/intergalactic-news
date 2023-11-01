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
in-depth and complex, while maintaining clarity and conciseness. Incorporate
main ideas and essential information, eliminating extraneous language and
focusing on critical aspects. Rely strictly on the provided text, without
including external information.

Transcript:
{transcript}

Your detailled summary:"""


SHORT_SUMMARY = """The following is a summarized transcript
of a youtube video by youtube channel {channel_name}. This is a channel that
talks mainly about astronomy and astrophysics and relevant news in these fields.

The title of the video is "{video_title}".

Write a very short summary of this transcript. The lenght of your summary should
not exceed 3 sentences. The language should be neutral and factual.

Summarized transcript:
{summary}

Your short summary:"""


TITLE_SUMMARY = """The following is a summarized transcript
of a youtube video by youtube channel {channel_name}. This is a channel that
talks mainly about astronomy and astrophysics and relevant news in these fields.

The title of the video is "{video_title}".

Write an alternative title to this video that fully conveys the topic of the video.
The language should be neutral, factual and not clickbaiting.

Summarized transcript:
{summary}

Your alternative title:"""


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
{summary}

Your summary tailored for the given audience:"""


# TODO
STORIES_SELECTION = """You are helping to generate content for a newsletter that aims
to update its readers on news in the fields of astronomy, astrophysics, physics
and space science in general.

You will be given a list numbered of youtube videos titles and a short summary
for each of them. The list will look like this:

1. [Title of the video]
[Summary of the video]

2. [Title of the video]
[Summary of the video]

...

Your task is to pick some of these videos based on their relevency to the topic of the
newsletter. There is no particlar number of videos expected in your answer: every videos
could be relevent to the topic (in which case you are expected to select all of them) as well
as none of them could be relevent.

You will give you answer in the form of a comma-separated list with only the
numbers of the videos that you choose, and nothing else. For example, if you are
given 10 different videos and you choose to pick videos number 1, 4, 5 and 9,
your answer should be: 1,4,5,9

If you decide to pick none of them, your answer should simply be: None

List of videos (titles and short summaries):
{titles_and_shorts}
Your selection:"""


# TODO
NEWSLETTER_SUMMARY = """

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


BASE_SUMMARY_EXAMPLE2 = """In this video, Anton Petrov discusses recent
groundbreaking discoveries about the human brain and neuronal complexity. The
discoveries are based on research conducted by the Neuroscience Multiomic Data
Archive (NEMO), which represents the largest collection of data on the human
brain. NEMO published 24 papers that focus on the individual cell types and
molecular interactions within the brain, creating the largest human brain atlas
to date.

The research revealed that there are over 3,000 different types of cells in the
human brain, each responsible for different functions and unique to specific
areas of the brain. This challenges the notion that the brain is composed only
of neurons and support cells. The focus of the research was not only on the
structure of the brain, but also on the molecular interactions between human and
non-human brains.

One surprising finding was that the older, deeper parts of the brain, such as
the brain stem, were found to be the most complex in terms of cell structure.
The cortex, which is often considered the more complex part of the brain
responsible for thinking, was found to be less complex in terms of cell
structure. The visual cortex, however, was found to be highly specialized and
distinct in humans, indicating our reliance on vision for navigating the world.

The research also revealed individual differences in cell proportions and gene
expression within the brain, making each human brain unique on a cellular and
genetic level. While the overall structure of the human brain is similar to that
of other animals, the genes controlling the connections between neurons and the
formation of circuits within the brain are different in humans.

The research aims to understand various brain disorders unique to humans, such
as depression, schizophrenia, and bipolar disorder. One study found a link
between certain brain cells and neuro-psychiatric disorders, suggesting a
genetic and molecular basis for these conditions.

Other discoveries include the identification of a protective layer in the brain
that controls the flow of cerebrospinal fluid, a different formation of axon
fibers in non-primate animals, and differences in brain development between
humans and other animals.

The research also explored the shape of the brain and its integration with the
skull. It found that humans have continuous integration and growth of the brain
throughout adulthood, whereas other animals, such as chimps, experience a more
static state once they reach adulthood.

The hippocampus, which plays a role in memory and visual imagination, was found
to be different in humans compared to other animals. The human hippocampus has
greater connections with visual areas of the brain, potentially explaining our
creativity and ability to imagine and visualize.

Overall, the research highlights the complexity of the human brain and its
unique characteristics compared to other animals. It also emphasizes the
importance of understanding the cellular and genetic aspects of the brain in
order to comprehend brain disorders and human intelligence. The limitations of
the studies include the use of tissue from deceased donors or surgical samples,
which may not fully represent a living, healthy human brain."""

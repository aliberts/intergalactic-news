import tiktoken
from unidecode import unidecode


def format_transcript(raw_transcript):
    transcript = " ".join(line["text"] for line in raw_transcript)
    transcript = unidecode(transcript).replace("\n", " ").replace("[Music]", "")
    return " ".join(transcript.split())


def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

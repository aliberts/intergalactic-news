from unidecode import unidecode


def format_transcript(raw_transcript):
    transcript = " ".join(line["text"] for line in raw_transcript)
    transcript = unidecode(transcript).replace("\n", " ").replace("[Music]", "")
    return " ".join(transcript.split())


def format_transcripts(raw_transcripts: dict) -> dict:
    return {
        video_id: format_transcript(raw_transcript)
        for video_id, raw_transcript in raw_transcripts.items()
    }

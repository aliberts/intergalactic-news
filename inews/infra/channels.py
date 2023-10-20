from dataclasses import dataclass
from typing import Optional

channel_ids = {
    "PBS Space Time": "UC7_gcs09iThXybpVgjHZ_7g",
    "Dr. Becky": "UCYNbYGl89UUowy8oXkipC-Q",
    "Anton Petrov": "UCciQ8wFcVoIIMi-lfu8-cjQ",
    "European Space Agency, ESA": "UCIBaDdAbGlFDeS33shmlD0A",
    "Scott Manley": "UCxzC4EngIsMrPmbm6Nxvb-A",
}


@dataclass
class YoutubeChannel:
    name: str
    id: str
    uploads_playlist_id: Optional[str] = None


yt_channels = {id: YoutubeChannel(name, id) for name, id in channel_ids.items()}

from typing import Annotated, Literal

from pydantic import StringConstraints

VideoID = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=11, max_length=11, pattern=r"[A-Za-z0-9_-]{11}"
    ),
]

UserGroup = Literal[0, 1, 2]

import os
from dataclasses import dataclass


@dataclass
class Config:
    API_SCHEME: str = os.getenv("DRAFTSMITH_API_SCHEME", "http")
    API_HOST: str = os.getenv("DRAFTSMITH_API_HOST", "vidar")
    API_PORT: int = int(os.getenv("DRAFTSMITH_API_PORT", "37240"))

    @classmethod
    def get_api_base_url(cls) -> str:
        return f"{cls.API_SCHEME}://{cls.API_HOST}:{cls.API_PORT}"

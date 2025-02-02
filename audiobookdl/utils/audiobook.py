import requests
from dataclasses import dataclass, field
from typing import Optional, Union

def add_if_value_exists(l: list[tuple[str, str]]):
    def add(key: str, value: Optional[str]):
        if value:
            l.append((key, value))
    return add


@dataclass(slots=True)
class Chapter:
    # Start time of chapter in milliseconds
    start: int
    # Title of chapter
    title: str


@dataclass(slots=True)
class Cover:
    image: bytes
    extension: str


@dataclass(slots=True)
class AESEncryption:
    key: bytes
    iv: bytes

AudiobookFileEncryption = AESEncryption

@dataclass(slots=True)
class AudiobookFile:
    # Url to audio file
    url: str
    # Output file extension
    ext: str
    # Title of file
    title: Optional[str] = None
    # Headers for request
    headers: dict[str, str] = field(default_factory=dict)
    # Encryption method
    encryption_method: Optional[AudiobookFileEncryption] = None



@dataclass(slots=True)
class AudiobookMetadata:
    title: str
    series: Optional[str] = None
    authors: list[str] = field(default_factory=list)
    narrators: list[str] = field(default_factory=list)

    def add_author(self, author: str):
        """Add author to metadata"""
        self.authors.append(author)

    def add_narrator(self, narrator: str):
        """Add narrator to metadata"""
        self.narrators.append(narrator)

    def add_authors(self, authors: list[str]):
        self.authors.extend(authors)

    def add_narrators(self, narrators: list[str]):
        self.narrators.extend(narrators)

    def all_properties(self, allow_duplicate_keys = False) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        add = add_if_value_exists(result)
        add("title", self.title)
        add("series", self.series)
        if allow_duplicate_keys:
            for author in self.author:
                result.append(("author", author))
            for narrator in self.narrator:
                result.append(("narrator", narrator))
        else:
            result.append(("author", self.author))
            result.append(("narrator", self.narrator))
        return result

    def all_properties_dict(self) -> dict[str, str]:
        result = {}
        for (key, value) in self.all_properties(allow_duplicate_keys=False):
            result[key] = value
        return result

    @property
    def author(self) -> str:
        """All authors concatenated into a single string"""
        return "; ".join(self.authors)

    @property
    def narrator(self) -> str:
        """All narrators concatenated into a single string"""
        return "; ".join(self.narrators)


@dataclass(slots=True)
class Audiobook:
    session: requests.Session
    metadata: AudiobookMetadata
    chapters: list[Chapter]
    files: list[AudiobookFile]
    cover: Optional[Cover]

    @property
    def title(self) -> str:
        return self.metadata.title

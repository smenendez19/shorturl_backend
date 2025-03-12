# Pydantic input models

# Imports

import re
from datetime import datetime
from typing import Optional

import pytz
from pydantic import BaseModel, field_validator, model_validator

utc = pytz.UTC


class ShortURLBody(BaseModel):
    url: Optional[str] = None
    expires_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def validate_if_one_parameter_is_present(cls, data):
        if len(data) == 0:
            raise ValueError("At least one parameter must be present")
        return data

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str):
        # Check if url is a valid page
        regex = r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
        if not re.match(regex, v):
            raise ValueError("url is not valid")
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: datetime):
        if v and v < datetime.now(v.tzinfo):
            raise ValueError("expires_at must be a future date")
        return v


class ShortURLBuildBody(BaseModel):
    url: str
    expires_at: Optional[datetime] = None

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: datetime):
        # Check future date
        if v and v < datetime.now(v.tzinfo):
            raise ValueError("expires_at must be a future date")
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str):
        # Check if url is a valid page
        regex = r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
        if not re.match(regex, v):
            raise ValueError("url is not valid")
        return v

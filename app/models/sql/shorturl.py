from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Field, SQLModel


class ShortURL(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    url: str
    visitors: Optional[int] = Field(default=0)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=datetime.now() + timedelta(days=90))

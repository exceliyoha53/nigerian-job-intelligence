from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from datetime import datetime


class Job(BaseModel):
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    job_url: str
    source: str
    scraped_at: datetime = None

    @field_validator('title', 'company', 'location')
    @classmethod
    def strip_and_validate(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v
    
    @field_validator('scraped_at', mode='before')
    @classmethod
    def set_scraped_at(cls, v):
        return v or datetime.utcnow()
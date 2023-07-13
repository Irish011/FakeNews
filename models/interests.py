from pydantic import BaseModel


class Interests(BaseModel):
    topics: str

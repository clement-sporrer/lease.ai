from pydantic import BaseModel


class Meta(BaseModel):
    total: int
    page: int
    per_page: int

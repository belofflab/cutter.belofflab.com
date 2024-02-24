from typing import List

from pydantic import BaseModel, RootModel
from pydantic.fields import Field

from pornhub_api.schemas.video import Video


class VideoSearchResult(BaseModel):
    RootModel: List[Video] = Field(..., alias="videos")

    def __iter__(self):
        return iter(self.RootModel)

    def __getitem__(self, item):
        return self.RootModel[item]

    def size(self):
        return len(self.RootModel)

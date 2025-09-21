# app/features/mount_skills/schemas.py
from __future__ import annotations
from typing import Literal, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

MountType = Literal["spears", "infantry", "archers"]

class Skill(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    description: str = Field(min_length=1)
    image: str = Field(
        pattern=r"^(spears|infantry|archers)\/[a-z0-9_\-\.]+\.(png|jpg|jpeg)$"
    )

class MountFile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # allow alias population

    mount_type: MountType
    defaults: dict = Field(default_factory=dict, alias="_defaults")
    slot1: List[Skill] = Field(default_factory=list)
    slot2: List[Skill] = Field(default_factory=list)

    @field_validator("slot1", "slot2")
    @classmethod
    def _no_duplicates(cls, v: List[Skill]):
        ids = [s.id for s in v]
        if len(ids) != len(set(ids)):
            dup = [x for x in ids if ids.count(x) > 1][0]
            raise ValueError(f"duplicate skill id in slot: {dup}")
        return v

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskFamily(str, Enum):
    API_PROTOCOL = "api_protocol"
    TOOL_EXECUTION = "tool_execution"
    AUTHORITY = "authority"


class ExecutionEpisode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    episode_id: str
    family: TaskFamily
    features: dict[str, Any]
    attempted_action: str
    observed_outcome: str
    better_action: str | None = None


class MemoryRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str
    family: TaskFamily
    conditions: dict[str, Any]
    action: str
    provenance: list[str] = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class BehavioralMemoryPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patch_version: str = "bmp/0.1"
    miner_strategy: str
    rules: list[MemoryRule]

    @field_validator("rules")
    @classmethod
    def bounded_rules(cls, value: list[MemoryRule]) -> list[MemoryRule]:
        if len(value) > 16:
            raise ValueError("BMP exceeds 16-rule MVP budget")
        return value


class MemoryFormationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    challenge_id: str
    episodes: list[ExecutionEpisode]
    task_family: TaskFamily | None = None
    memory_budget: int = Field(default=16, ge=0, le=16)
    policy_constraints: list[str] = Field(default_factory=list)
    evaluator_version: str = "consequent-eval/0.1"


class MemoryFormationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    challenge_id: str
    patch: BehavioralMemoryPatch

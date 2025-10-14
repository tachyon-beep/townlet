"""Observation configuration models."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class HybridObservationConfig(BaseModel):
    local_window: int = Field(11, ge=3, description="Odd window size for local observation slice")
    include_targets: bool = False
    time_ticks_per_day: int = Field(1440, ge=1)

    @model_validator(mode="after")
    def _validate_window(self) -> HybridObservationConfig:
        if self.local_window % 2 == 0:
            raise ValueError("observations.hybrid.local_window must be odd to center on agent")
        return self


class CompactObservationConfig(BaseModel):
    map_window: int = Field(7, ge=3)
    include_targets: bool = False
    object_channels: list[str] = Field(default_factory=list)
    normalize_counts: bool = True

    @model_validator(mode="after")
    def _validate_window(self) -> CompactObservationConfig:
        if self.map_window % 2 == 0:
            raise ValueError("observations.compact.map_window must be odd to center on agent")
        return self


class SocialSnippetConfig(BaseModel):
    top_friends: int = Field(2, ge=0, le=8)
    top_rivals: int = Field(2, ge=0, le=8)
    embed_dim: int = Field(8, ge=1, le=32)
    include_aggregates: bool = True

    @model_validator(mode="after")
    def _validate_totals(self) -> SocialSnippetConfig:
        if self.top_friends == 0 and self.top_rivals == 0:
            object.__setattr__(self, "include_aggregates", False)
        if self.top_friends + self.top_rivals > 8:
            raise ValueError("Sum of top_friends and top_rivals must be <= 8 for tensor budget")
        return self


class ObservationsConfig(BaseModel):
    """Bundle observation variants consumed by WorldObservationService."""

    hybrid: HybridObservationConfig = Field(
        default_factory=lambda: HybridObservationConfig(
            local_window=11,
            include_targets=False,
            time_ticks_per_day=1440,
        )
    )
    compact: CompactObservationConfig = Field(
        default_factory=lambda: CompactObservationConfig(
            map_window=7,
            include_targets=False,
            object_channels=[],
            normalize_counts=True,
        )
    )
    social_snippet: SocialSnippetConfig = Field(
        default_factory=lambda: SocialSnippetConfig(
            top_friends=2,
            top_rivals=2,
            embed_dim=8,
            include_aggregates=True,
        )
    )


__all__ = [
    "CompactObservationConfig",
    "HybridObservationConfig",
    "ObservationsConfig",
    "SocialSnippetConfig",
]

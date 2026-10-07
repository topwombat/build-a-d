"""The common discipline interface.

Every discipline returns its outputs together with (a) an error estimate and
(b) the list of conditions under which it should not be trusted. Error
estimates are expressed as independent multiplicative factors with a 1-sigma
relative value, which is what the Monte Carlo in ``ssbj.model.uncertainty``
samples. Correlations between factors are not modelled in Phase 1; see
docs/known_limits.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Uncertainty:
    """An independent multiplicative error factor applied to one model quantity.

    The factor is sampled as ``1 + sigma_rel * N(0, 1)`` (clipped to stay
    positive). ``basis`` says where the number comes from; when no validation
    data exists it must say so and the value must be conservative.
    """

    name: str
    sigma_rel: float
    basis: str
    applies_to: str = ""


@dataclass
class Validity:
    """Conditions under which a result should not be trusted, checked at run time."""

    discipline: str
    limits: list[str] = field(default_factory=list)  # static register entries
    warnings: list[str] = field(default_factory=list)  # triggered for this case

    def warn(self, msg: str) -> None:
        if msg not in self.warnings:
            self.warnings.append(msg)


@dataclass
class DisciplineResult:
    discipline: str
    method: str
    outputs: dict[str, Any]
    uncertainties: list[Uncertainty]
    validity: Validity

    def summary(self) -> dict[str, Any]:
        return {
            "discipline": self.discipline,
            "method": self.method,
            "uncertainties": [u.__dict__ for u in self.uncertainties],
            "not_trusted_when": self.validity.limits,
            "warnings": self.validity.warnings,
        }


@dataclass
class Factors:
    """Multiplicative factors sampled by the Monte Carlo; all 1.0 for the nominal case."""

    values: dict[str, float] = field(default_factory=dict)

    def __call__(self, name: str) -> float:
        return self.values.get(name, 1.0)

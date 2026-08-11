import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class Tier:
    """One step of a scorecard rule: past `threshold`, award `points`
    (and record `reason` if given). A list of tiers is checked in
    order — the first one that matches wins.
    """

    threshold: float
    points: int
    reason: Optional[str] = None


@dataclass(frozen=True)
class TravelIndexRules:
    high_min: float
    medium_min: float
    high_reason: str


@dataclass(frozen=True)
class FamilyIndexRules:
    high_min_ratio: float
    medium_min_ratio: float
    high_reason: str


@dataclass(frozen=True)
class SegmentRules:
    affluent_threshold: float
    vulnerable_threshold: float
    affluent_professional: str
    high_earner_low_discipline: str
    frugal_saver: str
    financially_vulnerable: str
    balanced_middle_income: str


@dataclass(frozen=True)
class ScorecardRules:
    """Every tunable number and label used by LifestyleIntelligenceService
    — income/savings/commitments thresholds, points, segment cutoffs and
    names. Nothing here is a Python literal in the service anymore: an
    admin (or a future settings screen, see FR-D5/D6/D7) can retune
    scoring without a code change or a redeploy, exactly like
    merchant_db.json already does for Enrichment.
    """

    score_cap: float
    affluence_income_tiers: List[Tier]
    affluence_savings_tiers: List[Tier]
    affluence_commitments_tiers: List[Tier]
    discipline_savings_tiers: List[Tier]
    discipline_atm_tiers: List[Tier]
    discipline_commitments_tiers: List[Tier]
    travel_index: TravelIndexRules
    family_index: FamilyIndexRules
    segments: SegmentRules


class ScorecardRulesRepository:
    """Gives access to the Lifestyle Intelligence scorecard rules.
    Same repository pattern as MerchantRepository/
    BusinessLifestyleRepository: the service doesn't know or care that
    this comes from a JSON file today.
    """

    def __init__(self, source_path: Path):
        self._source_path = source_path
        self._rules: Optional[ScorecardRules] = None

    def get_rules(self) -> ScorecardRules:
        if self._rules is None:
            self._rules = self._load()
        return self._rules

    def _load(self) -> ScorecardRules:
        with open(self._source_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def tiers(key: str) -> List[Tier]:
            return [Tier(**t) for t in data[key]]

        return ScorecardRules(
            score_cap=data["score_cap"],
            affluence_income_tiers=tiers("affluence_income_tiers"),
            affluence_savings_tiers=tiers("affluence_savings_tiers"),
            affluence_commitments_tiers=tiers("affluence_commitments_tiers"),
            discipline_savings_tiers=tiers("discipline_savings_tiers"),
            discipline_atm_tiers=tiers("discipline_atm_tiers"),
            discipline_commitments_tiers=tiers("discipline_commitments_tiers"),
            travel_index=TravelIndexRules(**data["travel_index"]),
            family_index=FamilyIndexRules(**data["family_index"]),
            segments=SegmentRules(**data["segments"]),
        )
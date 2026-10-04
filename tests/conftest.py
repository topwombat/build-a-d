import warnings
from pathlib import Path

import pytest

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
CONCORDE = ROOT / "ssbj" / "validation" / "concorde" / "case.yaml"


@pytest.fixture(scope="session")
def concorde_case():
    from ssbj.specs.schema import load_case

    return load_case(CONCORDE)


@pytest.fixture(scope="session")
def concorde_aircraft(concorde_case):
    from ssbj.geometry.parametric import build

    return build(concorde_case.design)

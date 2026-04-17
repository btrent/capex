"""Unit tests for the allocation math. No network calls."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

# Make the scripts/ dir importable
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from monthly_capex_report import (  # noqa: E402
    Engineer,
    allocate,
    parse_epic,
    parse_ticket,
    project_costs,
)

FIXTURE = Path(__file__).parent / "fixtures" / "sample_issues.json"


@pytest.fixture
def fixture_data() -> dict:
    return json.loads(FIXTURE.read_text())


@pytest.fixture
def cf(fixture_data) -> dict:
    return fixture_data["custom_fields"]


@pytest.fixture
def epics(fixture_data, cf) -> dict:
    return {e["key"]: parse_epic(e, cf) for e in fixture_data["epics"]}


@pytest.fixture
def tickets(fixture_data, cf) -> list:
    return [parse_ticket(i, cf) for i in fixture_data["issues"]]


@pytest.fixture
def engineers() -> dict:
    return {
        "user-alice": Engineer("user-alice", "Alice Chen", 15000.0),
        "user-bob": Engineer("user-bob", "Bob Singh", 12000.0),
        "user-carol": Engineer("user-carol", "Carol Nguyen", 18000.0),
        # Dana intentionally missing to exercise missing-engineer warning.
    }


@pytest.fixture
def month_range():
    return date(2026, 3, 1), date(2026, 3, 31)


# ---------------------------------------------------------------------------
# Basic allocation math
# ---------------------------------------------------------------------------
def test_basic_allocation_ratio_and_cost():
    """One engineer, 7 of 10 points capex -> ratio 0.7, $15k * 0.7 = $10.5k."""
    from monthly_capex_report import Epic, Ticket

    epics = {
        "E1": Epic("E1", "capex", "Yes", "Application Development", "P1", None),
    }
    tickets = [
        Ticket("T1", "u1", "User", 7, "E1", date(2026, 3, 5)),
        Ticket("T2", "u1", "User", 3, None, date(2026, 3, 10)),
    ]
    engineers = {"u1": Engineer("u1", "User", 15000.0)}
    allocs, warnings = allocate(tickets, epics, engineers, date(2026, 3, 1), date(2026, 3, 31))
    assert len(allocs) == 1
    a = allocs[0]
    assert a.capex_points == 7
    assert a.total_points == 10
    assert a.capex_ratio == pytest.approx(0.7)
    assert a.capex_cost == pytest.approx(10500.0)
    assert warnings == []


def test_multi_project_split_60_40():
    """10 capex points split 6/4 across two projects -> $ split 60/40."""
    from monthly_capex_report import Epic, Ticket

    epics = {
        "E1": Epic("E1", "", "Yes", "Application Development", "P1", None),
        "E2": Epic("E2", "", "Yes", "Application Development", "P2", None),
    }
    tickets = [
        Ticket("T1", "u1", "U", 6, "E1", date(2026, 3, 5)),
        Ticket("T2", "u1", "U", 4, "E2", date(2026, 3, 6)),
    ]
    engineers = {"u1": Engineer("u1", "U", 10000.0)}
    allocs, _ = allocate(tickets, epics, engineers, date(2026, 3, 1), date(2026, 3, 31))
    proj = project_costs(allocs)
    # All 10 points are capex -> ratio 1.0 -> capex_cost = 10000
    assert allocs[0].capex_cost == pytest.approx(10000.0)
    assert proj["P1"]["cost"] == pytest.approx(6000.0)
    assert proj["P2"]["cost"] == pytest.approx(4000.0)


def test_zero_point_fallback_emits_warning():
    """Ticket without story points treated as 1 point, warning emitted."""
    from monthly_capex_report import Epic, Ticket

    epics = {"E1": Epic("E1", "", "Yes", "Application Development", "P1", None)}
    tickets = [Ticket("T-no-sp", "u1", "U", None, "E1", date(2026, 3, 5))]
    engineers = {"u1": Engineer("u1", "U", 1000.0)}
    allocs, warnings = allocate(tickets, epics, engineers, date(2026, 3, 1), date(2026, 3, 31))
    assert allocs[0].capex_points == 1.0
    assert any(w.category == "missing_story_points" and w.ticket_key == "T-no-sp" for w in warnings)


def test_missing_engineer_skipped_with_warning(tickets, epics, month_range):
    """Assignee not in cost CSV -> skipped, warning emitted."""
    engineers = {
        "user-alice": Engineer("user-alice", "Alice", 15000.0),
        "user-bob": Engineer("user-bob", "Bob", 12000.0),
        "user-carol": Engineer("user-carol", "Carol", 18000.0),
    }
    allocs, warnings = allocate(tickets, epics, engineers, *month_range)
    engineer_names = {a.engineer.account_id for a in allocs}
    assert "user-dana" not in engineer_names
    assert any(w.category == "missing_engineer" and "user-dana" in w.message for w in warnings)


def test_zero_total_points_excluded_not_divide_by_zero():
    """Engineer with only None-point tickets on no epic -> still counted via fallback.
    But a fully-empty engineer (no tickets) is never in `totals` so never divides.
    """
    from monthly_capex_report import Ticket

    # No tickets means engineer never enters the allocation map.
    allocs, warnings = allocate([], {}, {"u1": Engineer("u1", "U", 1000.0)}, date(2026, 3, 1), date(2026, 3, 31))
    assert allocs == []

    # Ticket with no assignee is ignored (no divide-by-zero either).
    t = Ticket("T1", None, None, 5, None, date(2026, 3, 5))
    allocs, _ = allocate([t], {}, {}, date(2026, 3, 1), date(2026, 3, 31))
    assert allocs == []


def test_engineer_left_mid_month_prorated():
    """Engineer with end_date mid-month -> monthly cost prorated by days active."""
    from monthly_capex_report import Epic, Ticket

    epics = {"E1": Epic("E1", "", "Yes", "Application Development", "P1", None)}
    tickets = [Ticket("T1", "u1", "U", 10, "E1", date(2026, 3, 5))]
    # Active March 1-15: 15/31 days
    eng = Engineer("u1", "U", 31000.0, start_date=None, end_date=date(2026, 3, 15))
    allocs, _ = allocate(tickets, epics, {"u1": eng}, date(2026, 3, 1), date(2026, 3, 31))
    assert allocs[0].monthly_cost == pytest.approx(31000.0 * 15 / 31)
    # All 10 points capex -> ratio 1.0 -> capex_cost == prorated monthly cost
    assert allocs[0].capex_cost == pytest.approx(31000.0 * 15 / 31)


# ---------------------------------------------------------------------------
# Integration-ish: full fixture
# ---------------------------------------------------------------------------
def test_full_fixture_end_to_end(tickets, epics, engineers, month_range):
    """Sanity end-to-end: known fixture -> known totals."""
    allocs, warnings = allocate(tickets, epics, engineers, *month_range)
    by_id = {a.engineer.account_id: a for a in allocs}

    # Alice: SSO-1(5) + SSO-2(2) capex, MAINT-1(3) non-capex -> 7/10 = 0.7
    alice = by_id["user-alice"]
    assert alice.capex_points == 7
    assert alice.total_points == 10
    assert alice.capex_ratio == pytest.approx(0.7)
    assert alice.capex_cost == pytest.approx(15000.0 * 0.7)

    # Bob: SSO-3(3) capex, MAINT-2(2) non-capex -> 3/5 = 0.6
    bob = by_id["user-bob"]
    assert bob.capex_points == 3
    assert bob.total_points == 5
    assert bob.capex_cost == pytest.approx(12000.0 * 0.6)

    # Carol: RES-1(5) + RES-2(missing->1) both capex -> 6/6 = 1.0
    carol = by_id["user-carol"]
    assert carol.capex_points == 6
    assert carol.total_points == 6
    assert carol.capex_cost == pytest.approx(18000.0)

    # Dana missing from cost table
    assert "user-dana" not in by_id
    assert any(w.category == "missing_engineer" for w in warnings)
    assert any(w.category == "missing_story_points" for w in warnings)

    # Project rollup
    proj = project_costs(allocs)
    # SSO project: Alice 7pts + Bob 3pts
    assert proj["CAPEX-2026-PLATFORM-SSO"]["points"] == 10
    assert proj["CAPEX-2026-PLATFORM-SSO"]["cost"] == pytest.approx(alice.capex_cost + bob.capex_cost)
    # Resident app: Carol only
    assert proj["CAPEX-2026-RESIDENT-APP"]["cost"] == pytest.approx(18000.0)

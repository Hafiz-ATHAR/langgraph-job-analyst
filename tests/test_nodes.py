import pytest

from app.graph.agent import graph
from app.graph.utils.states import Analyst, AnalystTeam


class _StubLLM:
    """Stand-in for `get_llm()` that supports the chain used in nodes.py:
    `.with_structured_output(...).with_retry(...).invoke(...)`.
    """

    def __init__(self, response: AnalystTeam | BaseException) -> None:
        self._response = response

    def with_structured_output(self, schema: type) -> "_StubLLM":
        return self

    def with_retry(self, **kwargs: object) -> "_StubLLM":
        return self

    def invoke(self, messages: object) -> AnalystTeam:
        if isinstance(self._response, BaseException):
            raise self._response
        return self._response


def _patch_llm(
    monkeypatch: pytest.MonkeyPatch, response: AnalystTeam | BaseException
) -> None:
    monkeypatch.setattr(
        "app.graph.utils.nodes.get_llm",
        lambda: _StubLLM(response),
    )


def _initial_state(job_title: str) -> dict:
    return {
        "job_title": job_title,
        "analysts": [],
        "sections": [],
        "final_report": "",
    }


def _analyst(role: str) -> Analyst:
    return Analyst(
        name=f"Test {role}",
        role=role,
        description=f"{role} persona used in tests.",
        search_angle=f"{role.lower()} test angle 2026",
    )


def test_generate_analysts_returns_team_from_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    team = AnalystTeam(
        analysts=[_analyst("Salary Analyst"), _analyst("Skills Analyst")]
    )
    _patch_llm(monkeypatch, team)

    out = graph.nodes["generate_analysts"].invoke(
        _initial_state("Senior Python Engineer")
    )

    assert [a.role for a in out["analysts"]] == ["Salary Analyst", "Skills Analyst"]


def test_generate_analysts_returns_empty_on_llm_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_llm(monkeypatch, RuntimeError("LLM unavailable"))

    out = graph.nodes["generate_analysts"].invoke(
        _initial_state("Senior Python Engineer")
    )

    assert out == {"analysts": []}

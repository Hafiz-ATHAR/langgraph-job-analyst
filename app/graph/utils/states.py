from operator import add
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field


class Analyst(BaseModel):
    """A single analyst persona that investigates one angle of the job market."""

    name: str = Field(
        description="Full human-style name of the analyst, e.g. 'Maya Chen'."
    )
    role: str = Field(
        description="Short title describing the analyst's specialty, e.g. 'Salary Analyst', 'Skills Analyst', 'Hiring Trends Analyst'."
    )
    description: str = Field(
        description="One-to-two sentence summary of what this analyst investigates and why it matters to a job seeker."
    )
    search_angle: str = Field(
        description="Focused query angle this analyst will use for web search — concrete enough to drive a single search call."
    )


class AnalystTeam(BaseModel):
    """Team of analysts produced by the planner node; each analyst runs a parallel subgraph."""

    analysts: list[Analyst] = Field(
        description="Set of analysts covering distinct, non-overlapping angles of the target job market."
    )


class Section(BaseModel):
    """A single section of the final report, written by one analyst."""

    title: str = Field(
        description="Section heading, typically derived from the analyst's role."
    )
    content: str = Field(
        description="Markdown-formatted section body synthesized from the analyst's research."
    )


class AnalystOutputState(TypedDict):
    """Output channel of an analyst subgraph — only the produced section is bubbled up."""

    sections: Annotated[list[Section], add]


class OverallState(TypedDict):
    """Top-level graph state shared across the planner, analyst fan-out, and synthesizer."""

    job_title: str
    analysts: list[Analyst]
    sections: Annotated[list[Section], add]
    final_report: str


class AnalystState(TypedDict):
    """Per-analyst subgraph state used during search and section drafting."""

    job_title: str
    analyst: Analyst
    search_results: list[dict]
    sections: Annotated[list[Section], add]

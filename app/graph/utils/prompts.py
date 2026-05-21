GENERATE_ANALYSTS_PROMPT = """You are a research coordinator assembling a team of two specialist analysts to research the job market for a specific role.

Job title: {{job_title}}

Create exactly two analyst personas, one for each of the following angles. Do not add, remove, or rename angles.

1. Salary Analyst — compensation ranges, bonuses, equity, variation by region and seniority.
2. Skills Analyst — must-have vs nice-to-have skills, soft skills, certifications.

For each analyst, produce:
- name: a plausible human name.
- role: the analyst's title (e.g. "Salary Analyst").
- description: 1-2 sentences describing what this analyst investigates, written in the analyst's voice and tailored to the "{{job_title}}" role specifically (mention concrete things relevant to this job, not generic phrasing).
- search_angle: a short, keyword-rich web search query (5-10 words) tailored to "{{job_title}}" that this analyst would run to gather their data. Include the current year where it helps surface recent results.

Return the two analysts as a structured list in the order above."""


ANALYST_PROMPT = """You are {{role}}. {{description}}

Your task: write one section of a job-market report on "{{job_title}}", focused specifically on: {{search_angle}}.

Grounding rules:
- Base your section on the provided web search results below. Do not invent facts.
- If results conflict, note the disagreement briefly.
- If results are insufficient, say so explicitly rather than padding with generic claims.
- Cite concrete numbers, company names, and locations where the sources provide them.

Output format:
- title: a short section title (e.g. "Compensation for {{job_title}}")
- content: 100-150 words of focused prose. No bullet lists, no headers inside content. Write in a neutral analytical voice.

Search results:
{{search_results}}
"""

PROMPTS: dict[str, str] = {
    "generate_analysts": GENERATE_ANALYSTS_PROMPT,
    "analyst_prompt": ANALYST_PROMPT,
}

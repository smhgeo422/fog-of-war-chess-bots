"""Canonical Fog of War research IDs and variants.

Nine active scientific projects P1..P9; preserve all original A01..F99 records
and the Infra sentinel for historical integration smokes.
"""
import re

PROJECT = re.compile(r"P[1-9]")
LEGACY = re.compile(r"[A-F][0-9]{2}")
RESEARCH = re.compile(r"(?:P[1-9]|[A-F][0-9]{2}|Infra)")
VARIANT = re.compile(r"v(?:0|[1-9][0-9]*)")
SAFE_NAME = re.compile(r"[A-Za-z0-9_-]{1,100}")


def research_id(value):
    if not isinstance(value, str) or RESEARCH.fullmatch(value) is None:
        raise ValueError("invalid research ID: expected P1..P9, A01..F99, or Infra")
    return value


def research_variant(value, *, project=None):
    if value is None and not PROJECT.fullmatch(project or ""):
        return None
    if not isinstance(value, str) or VARIANT.fullmatch(value) is None:
        raise ValueError("P1..P9 research variants must be v0, v1, v2, ...")
    return value


def branch_identity(branch):
    """Read exact project/version from experiment/Px-vN-description.

    Legacy branches experiment/A01-... and experiment/Infra-... remain valid.
    """
    if not isinstance(branch, str) or not branch.startswith("experiment/"):
        raise ValueError("not an experiment branch")
    parts = branch[len("experiment/"):].split("-")
    project = research_id(parts[0])
    if PROJECT.fullmatch(project):
        if len(parts) < 3:
            raise ValueError("project experiment branch needs vN and description")
        version = research_variant(parts[1], project=project)
        if not all(SAFE_NAME.fullmatch(part) for part in parts[2:]):
            raise ValueError("invalid branch description")
        return project, version
    if len(parts) < 2 or not all(SAFE_NAME.fullmatch(part) for part in parts[1:]):
        raise ValueError("legacy experiment branch needs description")
    return project, None

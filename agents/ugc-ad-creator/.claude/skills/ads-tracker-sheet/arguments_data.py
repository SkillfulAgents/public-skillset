"""Positioning taxonomy for the tracker — loaded from /workspace/ads/arguments.json
(written by agent-onboarding, extended by ideate-ads as new angles appear).

Shape:
{
  "families": {"outcome": "Outcomes", "feature": "Features", "audience": "Audiences", "usecase": "Use Cases"},
  "arguments": [{"key": "outcome-save_time", "name": "Saves hours a week", "one_liner": "..."}]
}
Family = prefix of the key before the first '-'. Keep the file and the sheet's
Arguments tab in sync: new argument → add here first, then push to it.
"""
import json
import os
from pathlib import Path

ARGUMENTS_PATH = Path(os.environ.get("ADS_ARGUMENTS_PATH", "/workspace/ads/arguments.json"))


def _load():
    if not ARGUMENTS_PATH.exists():
        return {}, []
    data = json.loads(ARGUMENTS_PATH.read_text())
    fams = data.get("families", {})
    args = [(a["key"], a["name"], a.get("one_liner", "")) for a in data.get("arguments", [])]
    for k, _, _ in args:
        fams.setdefault(k.split("-", 1)[0], k.split("-", 1)[0].title())
    return fams, args


FAMILIES, ARGUMENTS = _load()
ARG_NAMES = {k: n for k, n, _ in ARGUMENTS}
ARG_KEYS = [k for k, _, _ in ARGUMENTS]


def family_of(key):
    return key.split("-", 1)[0]

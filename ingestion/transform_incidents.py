from __future__ import annotations

import re
from typing import Any, Iterable


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("body") or value.get("value") or value.get("name")
    if isinstance(value, list):
        value = "\n".join(item for item in (_text(item) for item in value) if item)
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def _comment_text(fields: dict[str, Any]) -> str | None:
    comments = fields.get("comment", {}).get("comments", [])
    values = []
    for comment in comments or []:
        body = _text(comment.get("body")) if isinstance(comment, dict) else _text(comment)
        if body:
            values.append(body)
    return "\n".join(values) or None


def _explicit_root_cause(fields: dict[str, Any], comments: str | None) -> str | None:
    for key, value in fields.items():
        normalized = re.sub(r"[^a-z0-9]", "", key.lower())
        if normalized in {"rootcause", "rootcauseanalysis", "rca"} or normalized.endswith("rootcause"):
            return _text(value)
    if comments:
        match = re.search(r"root\s*cause\s*[:\-]\s*(.+?)(?:\.|\n|$)", comments, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _search_text(record: dict[str, Any]) -> str:
    labels = (
        ("Incident ID", record.get("incident_id")),
        ("Title", record.get("title")),
        ("Description", record.get("description")),
        ("Comments", record.get("comments")),
        ("Root Cause", record.get("root_cause")),
        ("Resolution", record.get("resolution")),
        ("Project", record.get("project")),
        ("Component", record.get("component")),
        ("Status", record.get("status")),
    )
    return "\n".join(f"{label}: {value}" for label, value in labels if value)


def transform_issue(issue: dict[str, Any], source_url: str | None = None) -> dict[str, Any] | None:
    fields = issue.get("fields", issue)
    if not isinstance(fields, dict):
        return None

    incident_id = _text(issue.get("key") or issue.get("issue_key") or issue.get("id"))
    title = _text(fields.get("summary") or fields.get("title"))
    description = _text(fields.get("description") or fields.get("details"))
    if not incident_id or not title or not description:
        return None

    comments = _comment_text(fields)
    resolution = _text(fields.get("resolution"))
    project = fields.get("project") or {}
    components = fields.get("components") or []
    component_names = [_text(item.get("name")) for item in components if isinstance(item, dict)]
    record = {
        "incident_id": incident_id,
        "title": title,
        "description": description,
        "root_cause": _explicit_root_cause(fields, comments),
        "resolution": resolution,
        "comments": comments,
        "project": _text(project.get("key") or project.get("name")) if isinstance(project, dict) else _text(project),
        "component": ", ".join(item for item in component_names if item) or None,
        "service": _text(fields.get("service")),
        "severity": _text(fields.get("priority") or fields.get("severity")),
        "environment": _text(fields.get("environment")),
        "incident_type": _text(fields.get("issuetype") or fields.get("issueType")),
        "status": _text(fields.get("status")),
        "created_at": issue.get("created") or fields.get("created"),
        "updated_at": issue.get("updated") or fields.get("updated"),
        "source": "zenodo-public-jira-dataset",
        "source_url": source_url,
        "metadata": {"changelog": issue.get("changelog"), "raw_issue_id": issue.get("id")},
    }
    record["search_text"] = _search_text(record)
    return record


def transform_issues(issues: Iterable[dict[str, Any]], source_url: str | None = None) -> Iterable[dict[str, Any]]:
    for issue in issues:
        transformed = transform_issue(issue, source_url=source_url)
        if transformed:
            yield transformed

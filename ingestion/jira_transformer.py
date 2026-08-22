from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Iterable


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("body") or value.get("value") or value.get("name") or value.get("displayName")
    if isinstance(value, list):
        value = "\n".join(item for item in (_text(item) for item in value) if item)
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def _fields(issue: dict[str, Any]) -> dict[str, Any]:
    fields = issue.get("fields")
    return fields if isinstance(fields, dict) else issue


def _first(source: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in source and source[key] not in (None, "", []):
            return source[key]
    return None


def _comment_text(fields: dict[str, Any], issue: dict[str, Any]) -> str | None:
    value = _first(fields, "comment", "comments")
    if isinstance(value, dict):
        value = value.get("comments") or value.get("values")
    if not isinstance(value, list):
        value = [value] if value else []
    comments = []
    for comment in value:
        text = _text(comment.get("body") if isinstance(comment, dict) else comment)
        if text:
            comments.append(text)
    history = issue.get("changelog") or issue.get("history")
    if isinstance(history, dict):
        history = history.get("histories") or history.get("items")
    if isinstance(history, list):
        for item in history:
            text = _text(item)
            if text and text not in comments:
                comments.append(text)
    return "\n".join(comments) or None


def _named(value: Any) -> str | None:
    if isinstance(value, dict):
        return _text(_first(value, "key", "name", "value", "displayName"))
    return _text(value)


def _date(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


_LOW_QUALITY_TITLE_TERMS = (
    "anavar",
    "boldenona",
    "buy ",
    "casino",
    "cialis",
    "clenbuterol",
    "dianabol",
    "dublado",
    "genotropin",
    "gratis",
    "hgh ",
    "online",
    "porn",
    "proviron",
    "regarder",
    "roulette",
    "salbutamol",
    "slot ",
    "steroid",
    "streaming",
    "stanozolol",
    "sustanon",
    "testosterone",
    "testosterona",
    "trenbolone",
    "viagra",
    "winstrol",
    "xanax",
)


def _is_low_quality_title(title: str) -> bool:
    normalized = title.casefold()
    return any(term in normalized for term in _LOW_QUALITY_TITLE_TERMS)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value[:50]]
    return str(value)


def searchable_text(record: dict[str, Any]) -> str:
    labels = (
        ("Incident ID", record.get("incident_id")),
        ("Title", record.get("title")),
        ("Description", record.get("description")),
        ("Comments", record.get("comments")),
        ("Root Cause", record.get("root_cause")),
        ("Resolution", record.get("resolution")),
        ("Project", record.get("project")),
        ("Component", record.get("component")),
        ("Issue Type", record.get("incident_type")),
        ("Priority", record.get("severity")),
        ("Environment", record.get("environment")),
        ("Status", record.get("status")),
    )
    return "\n".join(f"{label}: {value}" for label, value in labels if value)


def transform_jira_issue(issue: dict[str, Any], source_url: str | None = None) -> dict[str, Any] | None:
    fields = _fields(issue)
    incident_id = _text(_first(issue, "key", "issue_key", "issueKey", "id") or _first(fields, "key", "issue_key"))
    title = _text(_first(fields, "summary", "title", "name"))
    description = _text(_first(fields, "description", "details", "text"))
    if not incident_id or not title:
        return None
    if _is_low_quality_title(title):
        return None

    comments = _comment_text(fields, issue)
    resolution_value = _first(fields, "resolution", "resolutionDescription", "resolution_description")
    resolution = _text(resolution_value)
    root_cause = None
    for key, value in fields.items():
        normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
        if normalized in {"rootcause", "rootcauseanalysis", "rca"} or normalized.endswith("rootcause"):
            root_cause = _text(value)
            break
    if root_cause is None and comments:
        match = re.search(r"root\s*cause\s*[:\-]\s*(.+?)(?:\.|\n|$)", comments, re.IGNORECASE)
        if match:
            root_cause = match.group(1).strip()

    project = _first(fields, "project", "projectKey", "projectname")
    components = _first(fields, "components", "component") or []
    if not isinstance(components, list):
        components = [components]
    component = ", ".join(item for item in (_named(value) for value in components) if item) or None
    record = {
        "incident_id": incident_id,
        "title": title,
        "description": description or "",
        "root_cause": root_cause,
        "resolution": resolution,
        "comments": comments,
        "project": _named(project),
        "component": component,
        "service": _text(_first(fields, "service", "serviceName")),
        "severity": _named(_first(fields, "priority", "severity")),
        "environment": _text(_first(fields, "environment", "env")),
        "incident_type": _named(_first(fields, "issuetype", "issueType", "type")),
        "status": _named(_first(fields, "status", "state")),
        "created_at": _date(_first(issue, "created", "created_at") or _first(fields, "created", "created_at")),
        "updated_at": _date(_first(issue, "updated", "updated_at") or _first(fields, "updated", "updated_at")),
        "source": "zenodo-public-jira-dataset-v7",
        "source_url": source_url,
        "metadata": {
            "raw_issue_id": _json_safe(issue.get("_id") or issue.get("id")),
            "issue_type": _json_safe(_first(fields, "issuetype", "issueType", "type")),
            "history": _json_safe(issue.get("changelog") or issue.get("history")),
        },
    }
    record["search_text"] = searchable_text(record)
    return record


def transform_jira_issues(issues: Iterable[dict[str, Any]], source_url: str | None = None) -> Iterable[dict[str, Any]]:
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        transformed = transform_jira_issue(issue, source_url=source_url)
        if transformed:
            yield transformed

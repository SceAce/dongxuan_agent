from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER = re.compile(r"\{([^{}]+)\}")


def get_path(data: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def matches(expression: dict[str, Any] | None, facts: dict[str, Any]) -> bool:
    if not expression:
        return True
    if "all" in expression:
        return all(matches(item, facts) for item in expression["all"])
    if "any" in expression:
        return any(matches(item, facts) for item in expression["any"])
    if "not" in expression:
        return not matches(expression["not"], facts)

    actual = get_path(facts, expression.get("path", ""))
    expected = expression.get("value")
    operator = expression.get("operator", "eq")
    if operator == "eq":
        return actual == expected
    if operator == "neq":
        return actual != expected
    if operator == "in":
        return actual in (expected or [])
    if operator == "not_in":
        return actual not in (expected or [])
    if operator == "contains":
        return _contains(actual, expected)
    if operator == "contains_any":
        return any(_contains(actual, item) for item in (expected or []))
    if operator == "truthy":
        return bool(actual)
    if operator == "not_empty":
        return bool(actual)
    if operator == "empty":
        return not actual
    if operator == "gte":
        return _number(actual) >= _number(expected)
    if operator == "gt":
        return _number(actual) > _number(expected)
    if operator == "lte":
        return _number(actual) <= _number(expected)
    if operator == "lt":
        return _number(actual) < _number(expected)
    if operator == "gt_path":
        return _number(actual) > _number(get_path(facts, str(expected)))
    if operator == "lt_path":
        return _number(actual) < _number(get_path(facts, str(expected)))
    if operator == "any_item_eq":
        return any(
            isinstance(item, dict) and item.get(expression.get("item_key")) == expected
            for item in (actual or [])
        )
    return False


def format_template(template: str, facts: dict[str, Any]) -> str:
    return _PLACEHOLDER.sub(
        lambda match: format_value(get_path(facts, match.group(1))),
        template,
    )


def format_value(value: Any, specification: dict[str, Any] | None = None) -> str:
    specification = specification or {}
    if specification.get("type") == "object_fields":
        fields = specification.get("fields") or []
        item_separator = specification.get("item_separator", "")
        separator = specification.get("separator", "、")
        return separator.join(
            item_separator.join(str(item.get(field, "")) for field in fields)
            for item in (value or [])
            if isinstance(item, dict)
        )
    if specification.get("type") == "join" or isinstance(value, (list, tuple, set)):
        separator = specification.get("separator", "、")
        return separator.join(str(item) for item in (value or []))
    if value is None:
        return ""
    return str(value)


def number(value: Any) -> float:
    return _number(value)


def _contains(container: Any, value: Any) -> bool:
    if container is None:
        return False
    try:
        return value in container
    except TypeError:
        return False


def _number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0

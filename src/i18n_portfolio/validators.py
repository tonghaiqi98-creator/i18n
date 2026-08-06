"""Deterministic validation helpers for i18n workflow outputs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re


PLACEHOLDER_PATTERN = re.compile(r"({{[^{}]+}}|\{[A-Za-z0-9_]+\}|%[sdif])")
KEY_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reason: str


def extract_placeholders(text: str) -> list[str]:
    """Return placeholders in their source form."""

    return PLACEHOLDER_PATTERN.findall(text)


def validate_placeholder_parity(source_text: str, candidate_text: str) -> ValidationResult:
    source_placeholders = Counter(extract_placeholders(source_text))
    candidate_placeholders = Counter(extract_placeholders(candidate_text))

    if source_placeholders == candidate_placeholders:
        return ValidationResult(True, "placeholder parity passed")

    missing = source_placeholders - candidate_placeholders
    extra = candidate_placeholders - source_placeholders
    details: list[str] = []
    if missing:
        details.append(f"missing={dict(missing)}")
    if extra:
        details.append(f"extra={dict(extra)}")

    return ValidationResult(False, "; ".join(details))


def validate_key_name(key: str, max_length: int = 64) -> ValidationResult:
    if not key:
        return ValidationResult(False, "key is empty")
    if len(key) > max_length:
        return ValidationResult(False, f"key length {len(key)} exceeds {max_length}")
    if not KEY_PATTERN.fullmatch(key):
        return ValidationResult(False, "key must be lower_snake_case and start with a letter")
    return ValidationResult(True, "key format passed")


def validate_length_limit(text: str, limit: int | None) -> ValidationResult:
    if limit is None:
        return ValidationResult(True, "no length limit")
    if len(text) <= limit:
        return ValidationResult(True, "length limit passed")
    return ValidationResult(False, f"text length {len(text)} exceeds {limit}")

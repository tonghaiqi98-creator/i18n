"""Small public demo of request planning and deterministic validation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any

from .validators import (
    ValidationResult,
    extract_placeholders,
    validate_key_name,
    validate_length_limit,
    validate_placeholder_parity,
)


@dataclass(frozen=True)
class TranslationRequest:
    device: str
    module: str
    key: str
    source_text: str
    char_limit: int | None
    target_languages: list[str]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TranslationRequest":
        return cls(
            device=str(payload["device"]),
            module=str(payload["module"]),
            key=str(payload.get("key", "")),
            source_text=str(payload["source_text"]),
            char_limit=payload.get("char_limit"),
            target_languages=list(payload["target_languages"]),
        )


def build_plan(request: TranslationRequest) -> dict[str, Any]:
    tasks: list[dict[str, Any]] = []
    if not request.key:
        tasks.append(
            {
                "type": "key_generation",
                "module": request.module,
                "constraints": ["lower_snake_case", "max_64_chars", "semantic_prefix"],
            }
        )

    tasks.append(
        {
            "type": "translation",
            "target_languages": request.target_languages,
            "constraints": {
                "placeholders": extract_placeholders(request.source_text),
                "char_limit": request.char_limit,
            },
        }
    )
    tasks.append({"type": "evaluation_gate", "checks": ["rules", "semantic_judge"]})
    tasks.append({"type": "delivery_adapter", "mode": "public_stub"})

    return {
        "device": request.device,
        "module": request.module,
        "requires_key_generation": not bool(request.key),
        "tasks": tasks,
    }


def run_rule_checks(
    request: TranslationRequest, candidate_key: str, candidate_text: str
) -> list[ValidationResult]:
    return [
        validate_key_name(candidate_key),
        validate_placeholder_parity(request.source_text, candidate_text),
        validate_length_limit(candidate_text, request.char_limit),
    ]


def load_request(path: Path) -> TranslationRequest:
    return TranslationRequest.from_dict(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python -m i18n_portfolio.pipeline <request.json>", file=sys.stderr)
        return 2

    request = load_request(Path(argv[1]))
    plan = build_plan(request)
    candidate_key = f"{request.module}_connect_wifi"
    candidate_text = request.source_text
    checks = run_rule_checks(request, candidate_key, candidate_text)

    print(
        json.dumps(
            {
                "plan": plan,
                "sample_candidate": {
                    "key": candidate_key,
                    "text": candidate_text,
                    "rule_checks": [check.__dict__ for check in checks],
                },
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

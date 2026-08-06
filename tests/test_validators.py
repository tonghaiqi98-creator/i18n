from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from i18n_portfolio.validators import (  # noqa: E402
    extract_placeholders,
    validate_key_name,
    validate_length_limit,
    validate_placeholder_parity,
)


class ValidatorTests(unittest.TestCase):
    def test_extracts_multiple_placeholder_styles(self) -> None:
        text = "Hello {{Name}}, retry in %d seconds from {screen_name}."
        self.assertEqual(
            extract_placeholders(text),
            ["{{Name}}", "%d", "{screen_name}"],
        )

    def test_placeholder_parity_passes_with_same_placeholders(self) -> None:
        result = validate_placeholder_parity(
            "Connect to {{WifiName}} with password {{WifiPassword}}.",
            "Verbinden mit {{WifiName}} und Passwort {{WifiPassword}}.",
        )
        self.assertTrue(result.passed)

    def test_placeholder_parity_fails_when_missing(self) -> None:
        result = validate_placeholder_parity(
            "Connect to {{WifiName}}.",
            "Connect to Wi-Fi.",
        )
        self.assertFalse(result.passed)
        self.assertIn("missing", result.reason)

    def test_key_name_requires_lower_snake_case(self) -> None:
        self.assertTrue(validate_key_name("camera_connection_retry").passed)
        self.assertFalse(validate_key_name("CameraConnectionRetry").passed)
        self.assertFalse(validate_key_name("camera-connection-retry").passed)

    def test_length_limit(self) -> None:
        self.assertTrue(validate_length_limit("short", 10).passed)
        self.assertFalse(validate_length_limit("too long", 3).passed)


if __name__ == "__main__":
    unittest.main()

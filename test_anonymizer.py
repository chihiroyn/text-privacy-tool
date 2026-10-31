import tempfile
import unittest
from pathlib import Path

from anonymizer import (
    MappingError,
    default_output_path,
    anonymize,
    load_replacements,
)


class LoadReplacementsTest(unittest.TestCase):
    def write_csv(self, content: str) -> Path:
        path = Path(self.tempdir.name) / "mapping.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_loads_quoted_values_and_keeps_order(self) -> None:
        path = self.write_csv('original,replacement\n"山田,太郎",利用者A\n')
        self.assertEqual(
            load_replacements(path)[0].original,
            "山田,太郎",
        )

    def test_rejects_empty_original(self) -> None:
        path = self.write_csv("original,replacement\n,利用者A\n")
        with self.assertRaises(MappingError):
            load_replacements(path)

    def test_rejects_duplicate_original(self) -> None:
        path = self.write_csv("original,replacement\n山田,利用者A\n山田,利用者B\n")
        with self.assertRaises(MappingError):
            load_replacements(path)

    def test_builds_output_path_next_to_input(self) -> None:
        self.assertEqual(
            default_output_path(Path("/tmp/input.txt")),
            Path("/tmp/input_anonymized.txt"),
        )

    def test_anonymize_preserves_exact_text_layout(self) -> None:
        mapping = self.write_csv("original,replacement\n山田,利用者A\n")
        source = Path(self.tempdir.name) / "input.txt"
        output = default_output_path(source)
        cases = [
            "", "山田", "変更なし", "\ufeff山田\r\n",
            "\r\n山田\n\n  山田\r末尾\t",
        ]
        for newline in ("\n", "\r\n", "\r"):
            for ending in ("", newline, newline * 2):
                cases.append(newline + "  山田\t" + newline * 3 + "山田" + ending)
        for content in cases:
            with self.subTest(content=repr(content)):
                original = content.encode("utf-8")
                source.write_bytes(original)
                anonymize(source, mapping, output)
                self.assertEqual(
                    output.read_bytes(), content.replace("山田", "利用者A").encode("utf-8")
                )
                self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()

"""CSVで指定した変換リストを使ってテキストを匿名化する。"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Replacement:
    """匿名化前の文字列と匿名化後の文字列。"""

    original: str
    replacement: str


class MappingError(ValueError):
    """変換リストの形式が不正な場合に発生する。"""


TEXT_SUFFIXES = {
    "", ".txt", ".text", ".log", ".rst", ".asc",
    ".md", ".markdown", ".csv", ".tsv", ".json",
}


def load_replacements(path: Path) -> list[Replacement]:
    """変換リストCSVを読み込み、置換順を保った一覧として返す。"""
    replacements: list[Replacement] = []

    # BOM付きUTF-8も扱えるようにし、CSVの引用符やカンマは標準機能に任せる。
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["original", "replacement"]:
            raise MappingError(
                "CSVのヘッダーは original,replacement で指定してください"
            )

        for line_number, row in enumerate(reader, start=2):
            original = row["original"]
            replacement = row["replacement"]
            if not original:
                raise MappingError(f"{line_number}行目: original は空にできません")
            if replacement is None:
                raise MappingError(f"{line_number}行目: replacement がありません")
            replacements.append(Replacement(original, replacement))

    if not replacements:
        raise MappingError("変換リストに変換規則がありません")

    originals = [item.original for item in replacements]
    if len(originals) != len(set(originals)):
        raise MappingError("original に重複した値があります")
    return replacements


def anonymize(input_path: Path, mapping_path: Path, output_path: Path) -> None:
    """CSVの順番で置換する。UTF-8テキストでは元の改行を保持する。"""
    if input_path.resolve() == output_path.resolve():
        raise ValueError("入力ファイルと出力ファイルには別のパスを指定してください")

    try:
        import polydoc
    except ImportError as error:
        raise RuntimeError(
            "polydoc がインストールされていません。"
            "python -m pip install -r requirements.txt を実行してください"
        ) from error

    replacements = load_replacements(mapping_path)
    if input_path.suffix.lower() in TEXT_SUFFIXES:
        from polydoc.model import Document, Paragraph, Text

        # 文書解析・整形による改行の消失を避け、元の文字列全体を置換対象にする。
        # バイト単位の入出力で改行変換を避け、UTF-8のBOMもそのまま保持する。
        paragraph = Paragraph([Text(input_path.read_bytes().decode("utf-8"))])
        document = Document([paragraph])
        for item in replacements:
            document.replace_text(item.original, item.replacement)
        output_path.write_bytes(paragraph.text.encode("utf-8"))
        return

    # polydocを使うことで、単純なテキストだけでなく対応形式の文書も同じ手順で扱う。
    document = polydoc.open(input_path)
    for item in replacements:
        document.replace_text(item.original, item.replacement)
    document.save(output_path)


def default_output_path(input_path: Path) -> Path:
    """入力ファイルを残したまま匿名化結果を保存するパスを作る。"""
    return input_path.with_name(f"{input_path.stem}_anonymized{input_path.suffix}")


def build_parser() -> argparse.ArgumentParser:
    """CUI引数を定義する。"""
    parser = argparse.ArgumentParser(
        description="CSVの変換リストに従ってテキスト、Excel、Wordファイルを変換します。"
    )
    parser.add_argument(
        "input", type=Path, help="変換対象のテキスト、Excel、またはWordファイル"
    )
    parser.add_argument("mapping", type=Path, help="変換リストCSV")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CUIのエントリーポイント。"""
    args = build_parser().parse_args(argv)
    try:
        anonymize(args.input, args.mapping, default_output_path(args.input))
    except (OSError, MappingError, RuntimeError, ValueError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

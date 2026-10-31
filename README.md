# text-privacy-tool

CSVの変換リストに従って、テキスト、Excel、Wordファイルに含まれる情報を変換するCUIツールです。文字列置換と各文書形式の読み書きには `polydoc` を使用します。

UTF-8テキスト（`.txt`、`.text`、`.log`、`.rst`、`.asc`、`.md`、`.markdown`、`.csv`、`.tsv`、`.json`、拡張子なし）は、改行コード（LF／CRLF／CR、混在も含む）、空行、空白、末尾改行の有無、BOMを保持します。変換規則自体に改行が含まれる場合は、その規則に従って変更されます。その他の文書形式は `polydoc` の読み込み・保存を使用します。

## セットアップ

```bash
python -m pip install -r requirements.txt
```

## 変換リスト

UTF-8のCSVを用意してください。ヘッダーは `original,replacement` 固定です。`original` が空の行と、同じ `original` の重複はエラーになります。CSVの上から順に置換します。

```csv
original,replacement
山田太郎,利用者A
tarou@example.com,user-a@example.invalid
```

## 実行

```bash
python anonymizer.py input.txt mapping.csv
```

Excelファイルは次のように実行できます。

```bash
python anonymizer.py input.xlsx mapping.csv
```

Wordファイルは次のように実行できます。

```bash
python anonymizer.py input.docx mapping.csv
```

出力ファイルは入力と同じディレクトリに、`<入力ファイル名>_anonymized<拡張子>` として自動生成されます。たとえば `input.txt` の場合は `input_anonymized.txt`、`input.xlsx` の場合は `input_anonymized.xlsx`、`input.docx` の場合は `input_anonymized.docx` になります。入力ファイルは上書きしないため、元のExcel・Wordファイルは変更されません。出力先が既存ファイルの場合は上書きされます。

Excelでは、各ワークシートのセル内テキストが置換対象です。Excelの読み書きには `polydoc[xlsx]` の追加依存関係が必要です。

Wordでは、本文・表・ヘッダー・フッターなどのテキストが置換対象です。Wordの読み書きには `polydoc[docx]` の追加依存関係が必要です。

## サンプル

サンプルは `samples/` フォルダにあります。

```bash
python anonymizer.py samples/input.txt samples/mapping.csv
```

実行すると `samples/input_anonymized.txt` が生成されます。

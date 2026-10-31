# text-privacy-tool

CSVの変換リストに従って、テキストファイルに含まれる個人情報を匿名化するCUIツールです。文字列置換には `polydoc` を使用します。

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

入力には、`polydoc` が対応するテキスト系ファイルを指定できます。出力ファイルは入力と同じディレクトリに、`<入力ファイル名>_anonymized<拡張子>` として自動生成されます。たとえば `input.txt` の場合は `input_anonymized.txt` になります。出力先が既存ファイルの場合は上書きされます。

## サンプル

サンプルは `samples/` フォルダにあります。

```bash
python anonymizer.py samples/input.txt samples/mapping.csv
```

実行すると `samples/input_anonymized.txt` が生成されます。

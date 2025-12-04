# kaigitai

散在する団体・会議のデータを集約し、登録から閲覧までを支援するPython製ツールセットです。`register/` に入力したJSONを検証しつつ `data/` 用に整形し、Flaskベースの管理UIと静的ビューアで閲覧できます。

## セットアップ

- 必要環境: Python 3.11 以上、[uv](https://github.com/astral-sh/uv) 推奨
- 依存関係のインストール:

```bash
uv sync
```

以降のコマンドは `uv run ...` で実行できます。

## データ登録の基本フロー

1. `register/group|person|meeting/form.json` を編集（name参照でOK、id空で可）  
   - これらのJSONは「一括登録用フォーム」として扱います。GUI入力を使う場合は後述の管理UIでの作成/編集も可能です。
2. 変換: `uv run python cli.py` → `1` を選択  
   - `dry-run` で出力予定の確認、`strict` で未登録 name をエラー扱い
3. 生成物確認: `data/group/*.json`, `data/person/*.json`, `data/meeting/{uuid}/basic.json`
4. 検証のみ: `uv run python cli.py` → `2`
5. nameフラグメント生成: `uv run python cli.py` → `3`（`docs/schema/fragment/` 出力）

詳細手順や雛形は `docs/manual/register_to_data.md` を参照してください。

## CLI の概要

```bash
uv run python cli.py
```

- `1) register→data 変換`: register を data 用JSONへ変換。UUID採番、参照解決、スキーマ検証を実施。
- `2) スキーマ検証のみ`: register/data の既存ファイルを JSON Schema で検証。
- `3) fragment生成`: 登録済み name 一覧を `docs/schema/fragment/*.json` に出力。

## 管理UIとビューア

- 管理UI（CRUD・検証付き）: `uv run app.py` を起動し、ブラウザでアクセス。
- 閲覧専用ビューア: `uv run viewer.py` でローカル閲覧。GitHub Pages 用静的出力は以下。

```bash
rm -rf build
UV_CACHE_DIR=/tmp/uv-cache uv run scripts/freeze_viewer.py
```

静的版は `/kaigitai` をベースパスとしてリンクが生成されます。

## テスト

```bash
uv run pytest
```

## ディレクトリ構成

- `register/`: 編集用JSON（group/person/meeting）
- `data/`: 変換済みデータ出力先
- `docs/spec/`: 仕様書（概要・ER・フロー・スキーマ運用）
- `docs/schema/`: JSON Schema（base/fragment）
- `scripts/freeze_viewer.py`: 静的ビューア出力スクリプト

## 参考ドキュメント

- プロジェクト概要: `docs/spec/001_overview.md`
- フローと運用: `docs/spec/003_flow.md`
- スキーマ運用: `docs/spec/004_json_schema.md`
- 変換手順: `docs/manual/register_to_data.md`

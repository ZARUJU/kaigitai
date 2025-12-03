# JSONスキーマ運用（ドラフト）

## 1. 目的
- 入力補完やバリデーションに利用するJSON Schemaを定義し、`register/`（下書き）と`data/`（確定）の双方で使えるようにする
- スキーマ変更時にIDE補完・CLI検証を即時反映できる手順を明文化する

## 2. 対象とファイル配置
- 対象モデル：`GROUP` / `MEETING` / `PERSON`（およびMEETING配下の `main`/`sub`/`attendee`/`sources`/`materials`）
- ディレクトリ構成：`docs/schema/base/` にメインスキーマ（register用・data用）、`docs/schema/fragment/` に自動生成される参照用スキーマ（例：グループ名の enum など）を配置
- 利用先：IDEのJSONスキーマ設定（VS Codeなら`$schema`）、CLIの検証処理

## 3. スキーマの考え方
- register用（下書き）：`id` 未指定を許容し、`group_id` や `attendee` などの参照は name 記述を許容。複数件を1ファイルにまとめて書くケースも許容。
- data用（確定）：各エンティティ1件ごとに UUID 必須、参照は UUID のみ。ファイル配置は `data/{entity}/{uuid}.json`（MEETINGのみ `data/meeting/{uuid}/...` に分割）。
- MEETINGはファイル構成に合わせてスキーマを分割：`meeting.basic.schema.json`（`id/main/sub/date/holding/start_time/end_time/agenda/sources/materials` など必須コア）と、必要に応じて拡張スキーマ（例：`meeting.transcript.schema.json` など）を用途別に用意
- 共通：必須/任意、enum（`holding`、`source_type`）、フォーマット（日付`yyyy-mm-dd`、時刻`hh:mm`、URL）、文字列トリム後非空の表現を定義

## 4. 実装手順（たたき台）
- JSON Schemaドラフトバージョン：Draft 2020-12（または Draft-07）を採用（決める）
- スキーマ作成：まず register 用を定義し、data 用は `$ref` で共通部を再利用
- 補完用の例示：`examples` もしくは `default` で典型値を示す
- CLI検証：生成・変換時にスキーマバリデーションを走らせる（将来追加）

## 5. 今後決めること
- 採用するドラフトバージョン（Draft-07 / 2020-12）
- `docs/schema/` の命名や階層（単一ファイルにまとめるか、モデル別に分けるか）
- VS Code向け設定サンプル（`$schema` 設定や `json.schemas` の例）
- CLI検証実装の要否とコマンド仕様

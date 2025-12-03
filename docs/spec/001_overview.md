# 概要

- 開発言語：Python
- データ管理：json
- 主要ライブラリ
  - FastAPI: API作成、閲覧サイト
  - pydantic: 型定義

## ドキュメントインデックス

| ファイル | 目的 |
| --- | --- |
| `docs/spec/001_overview.md` / `001_overview.md` | このプロジェクト概要 |
| `docs/spec/002_er_and_schema.md` / `002_er_and_schema.md` | ERとフィールド仕様（GROUP/MEETING/PERSON、main/sub含む） |
| `docs/spec/003_flow.md` / `003_flow.md` | 登録/編集フローと運用（register→CLI→data） |
| `docs/spec/004_json_schema.md` / `004_json_schema.md` | JSONスキーマ運用（base/fragment配置と補完・検証方針） |

## 作成予定のプログラム

- JSONスキーマ生成・検証CLI（register→data変換、name→UUID解決、スキーマ検証）
- データ登録/更新用CLI（登録用JSONにUUID採番、`data/` 出力、整合性チェック）
- FastAPIベースのAPI・閲覧サイト（データ提供と閲覧UI）

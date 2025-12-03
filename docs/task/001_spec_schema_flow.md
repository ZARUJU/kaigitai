# GOAL： データスキーマと登録/編集フローの仕様策定

# ユーザーからの依頼
- スキーマと登録・編集フローの仕様書を作成する
- 現時点の利用者は開発者本人、将来的に全体へ公開
- 検索要件は後日検討
- 会議情報の更新は会議ごとに手動で実施
- 全データを公開する

# タスク
## 現状（完了後の状態）
- `docs/spec/001_overview.md` にドキュメントインデックスと予定プログラムを追記
- `docs/spec/002_er_and_schema.md` で GROUP/MEETING/PERSON のスキーマを定義（main/sub、agenda配列、materialsをbasicに含む、データ配置方針）
- `docs/spec/003_flow.md` で register→CLI→data の登録/編集フローを整理
- `docs/spec/004_json_schema.md` で register用とdata用スキーマの違い、MEETING basic/拡張、base/fragment 配置を記載
- `docs/spec/005_cli.md` で CLIメニュー・配置・name解決・検証順序・差分表示・テスト方針を記載

## 変更後（達成したこと）
- スキーマ仕様（必須/任意/型/ID採番/参照整合性/データ配置）を文書化
- 手動更新フローと運用ルールを明確化（固定パス、register下書き→UUID採番・name解決→data出力）
- JSONスキーマの運用方針とCLI設計を決定し、実装準備の指針を提示

## 手順（今回実施した流れ）
- ERとフィールド仕様を整理し、main/sub構造やagenda配列、materialsをbasicへ反映
- データ保存構成を決定（GROUP/PERSONは `data/{entity}/{uuid}.json`、MEETINGは `data/meeting/{uuid}/basic.json` など分割）
- JSONスキーマ方針を策定（register用とdata用の差異、MEETING basicと拡張、base/fragment配置）
- CLI仕様を策定（メニュー1〜3、サブコマンド構成、name→UUID解決戦略、バリデーション順序、差分/dry-run、テスト方針）

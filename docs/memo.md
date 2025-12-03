# MEMO

- meeting拡張スキーマ・処理（逐語録/transcriptや追加資料など）は未実装。必要になったら `docs/schema/base/meeting.*.data.schema.json` を追加し、convertに拡張ファイル出力を組み込む。
- CLIの差分表示は簡易（作成/更新/スキップ数＋dry-run出力パス）。細かい差分を確認したい場合は後続で実装する。
- name解決のstrict/緩和は会議（meeting）で選択可能。group/person未登録の場合の動作を拡張するなら resolver を拡張する。

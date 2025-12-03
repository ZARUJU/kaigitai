# GOAL
- CLIのデータ登録機能を実装する（register→data変換）
- JSONスキーマを整備する（register用/data用、meeting basic分割に対応）
- フローに関するマニュアルを `docs/manual/` に作成する

# ユーザーからの依頼
- CLIのデータ登録機能（register→data変換）を実装する
- JSONスキーマを整備する（register用/data用、meeting basic分割に対応）
- フローに関するマニュアルを `docs/manual/` に作成する

# タスク
## 現状（完了したこと）
- [x] スキーマ整備：register/data 用の JSON Schema を追加（group/person/meeting basic）
- [x] CLI実装：convert/validate/fragment サブコマンドを実装し、register→data 変換・スキーマ検証・fragment生成が動作
- [x] ユーティリティ：resolver/validator/writer/loader/utils を実装
- [x] マニュアル：`docs/manual/register_to_data.md` に手順とコピペ用雛形を記載
- [x] VS Code設定：`.vscode/settings.json` にスキーマ紐付けを追加
- [x] テスト：`tests/test_schema.py` と `tests/test_convert.py` を追加、`uv run pytest` 成功

## 今後やること（残タスク）
- [x] dry-run/差分表示の実装（現在は未対応）→ dry-runモード追加、出力予定パスを表示
- [x] name解決ポリシーの調整（未登録 name を自動追加するかどうかのモード切り替え）→ meeting変換で strict選択可
- [x] convert 実行時のログ出力を整備（新規UUID、解決結果のサマリ表示など）→ 作成/更新/スキップ/エラー表示を追加
- [ ] 必要に応じて meeting 拡張ファイル（逐語録など）用スキーマ/処理を追加

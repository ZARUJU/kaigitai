# GOAL
- Flaskベースの管理用UI（register編集・data閲覧）の仕様策定と実装
- app向け仕様ドキュメントの作成
- 必要に応じてFastAPI読み取り専用APIへの接続方針を整理する（実装は別タスクでも可）

# ユーザーからの依頼
- taskを作り、仕様を定義し、実装する流れで進める
- appはFlask、APIはFastAPI（GETのみ）で分ける想定

# タスク
## 現状
- `app.py` に Flask UIを追加（現状は register編集＋data閲覧のインラインテンプレート）
- 依存に Flask を追加済み
- スキーマ/CLI/マニュアル/テストは整備済み

## 変更後
- app向け仕様ドキュメントを作成し、画面/エンドポイント/バリデーション/データフローを明文化（フォームCRUD前提）
- register直接編集は廃止し、group/person/meeting の一覧・詳細・新規・編集・削除をフォームで実装
- groupのツリー表示画面を追加
- テンプレート/コンポーネントを `templates/` に分割
- FastAPI側（読み取り専用）の位置づけを整理（実装は別タスクで扱ってもよい）

## 手順
- app仕様書を作成（例：`docs/spec/006_app.md`）にUIフロー・エンドポイント・入力/出力・テンプレート/コンポーネント方針を記載
- register直接編集を廃止し、CRUDルーティングとフォーム仕様を明確化
- `templates/` 配下へ共通レイアウト・部分テンプレートを分割し、app.py から `render_template` で利用する
- 必要なUI改修を app.py に反映（一覧/詳細/新規/編集/削除、tree表示、フォームUX、エラー表示、リダイレクト）
- FastAPI read-only APIの方針をメモ化し、着手が必要なら別タスクを起票する

## 現状の進捗メモ
- app.py をCRUDルーティングに置き換え、IDは新規時に自動採番
- group/person/meeting の一覧・詳細・新規・編集・削除をテンプレート化（Tailwind, templates/配下）
- meetingフォームに検索付きdatalistと行追加/削除を実装（attendee、sub、main）
- meeting detail/list の表示をカードコンポーネント化し、リンク整備（group/personへの導線）
- group詳細で会議一覧を表示し、会議追加リンクを用意
- groupツリー表示、子団体ツリー `group/<id>/children` を追加
- parent表示は name(id) 形式でリンク化

## 残タスク
- [x] 会議一覧の並び順・絞り込み対応（例：日付降順、簡易検索フォーム）
- [x] フォームのUIバリデーション強化（必須/形式の即時フィードバックはブラウザ標準で対応）
- [x] datalist表示のラベル改善（`name (id)` 形式：parent/meetingフォームのgroup選択、attendee/person選択など）
- [x] 仕様ドキュメント（006_app.md）を最新状態に更新
- [x] Person削除時に、出席者として紐づく会議がある場合のアラートと、自分自身をattendeeから外すかを確認するダイアログ/フローを追加

# register→data 変換マニュアル（ドラフト）

## 前提
- 入力：
  - `register/group/form.json`
  - `register/person/form.json`
  - `register/meeting/form.json`
- 出力：
  - `data/group/{uuid}.json`
  - `data/person/{uuid}.json`
  - `data/meeting/{uuid}/basic.json`
- スキーマ：
  - 以下の２つを利用
    - `docs/schema/base/*.register.schema.json`
    - `*.data.schema.json`

## 手順
1. registerフォームを編集（name参照でOK、idは空でよい）
2. CLI実行：`python cli.py` → `1`（register→data 変換）
3. 生成結果を確認
   - group/person: `data/{entity}/{uuid}.json`
   - meeting: `data/meeting/{uuid}/basic.json`
4. 必要に応じて `python cli.py` → `2` でスキーマ検証のみ実行
5. フラグメント生成：`python cli.py` → `3`（nameのenumを `docs/schema/fragment/` に出力）

## ログと挙動
- 未登録nameを参照するとエラー（meetingのmain/sub/attendee）。先にgroup/personを登録してからmeetingを流す
- id未指定の場合は UUID が自動採番される
- meetingは main/sub を UUID に解決し、attendee も UUID 配列に解決する

## 雛形（コピペ用）

### group/form.json
```json
[
  {
    "name": "団体名",
    "category": "区分",
    "official_url": "https://example.com/group",
    "parent": null,
    "list_url": null
  }
]
```

### person/form.json
```json
[
  {
    "name": "氏名",
    "name_yomi": null
  }
]
```

### meeting/form.json（basic）
```json
[
  {
    "main": { "group_id": "団体名または合同委員会名", "num": 1 },
    "sub": [
      { "group_id": "合同先A", "num": 1 }
    ],
    "date": "2024-01-01",
    "holding": "onsite",
    "start_time": "10:00",
    "end_time": "12:00",
    "agenda": ["議題1", "議題2"],
    "attendee": ["氏名A", "氏名B"],
    "sources": [
      { "url": "https://example.com/meeting/1", "source_type": "meeting_page", "title": null }
    ],
    "materials": [
      { "url": "https://example.com/materials/1.pdf", "title": "資料1" }
    ]
  }
]
```
## テスト実行（推奨）
- `uv run pytest` でテストを実行（将来的に追加予定）

# register→data 変換マニュアル

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
  - `docs/schema/base/*.register.schema.json`
  - `docs/schema/base/*.data.schema.json`
- 変換・検証は `uv run python cli.py` で実行する
- GUIで登録・編集する場合：`uv run app.py`（Flask管理UI）を起動してブラウザ操作

## 手順（基本フロー）
1. `register/` を編集（name参照でOK、idは空でよい。sourcesは必ずURLを入れる）
2. 変換：`uv run python cli.py` → `1`（register→data 変換）
3. 生成結果確認
   - group/person: `data/{entity}/{uuid}.json`
   - meeting: `data/meeting/{uuid}/basic.json`
4. 検証のみ実行：`uv run python cli.py` → `2`
5. nameフラグメント生成：`uv run python cli.py` → `3`（`docs/schema/fragment/` に出力）

## ログと挙動
- 未登録nameを参照するとエラー（meetingのmain/sub/attendee）。先にgroup/personを登録してからmeetingを流す
- id未指定の場合は UUID 自動採番
- meetingでは main/sub を UUID 解決し、attendee も UUID 配列に解決する
  - sources はオブジェクト形式（`meeting_page` / `transcript` / `announcement` / `other[]`）

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
    "sources": {
      "meeting_page": "https://example.com/meeting/1",
      "transcript": "https://example.com/minutes/1",
      "announcement": "https://example.com/notice/1",
      "other": [
        { "url": "https://example.com/other.pdf", "title": "その他資料" }
      ]
    },
    "materials": [
      { "url": "https://example.com/materials/1.pdf", "title": "資料1" }
    ]
  }
]
```

## 静的ビルド（閲覧用 viewer）
- GitHub Pages 用に静的出力する場合：
  - `rm -rf build`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run scripts/freeze_viewer.py`
- ベースパスは `/kaigitai` を前提にリンクが生成される
- Actions: `.github/workflows/deploy-pages.yml`（mainへのpushで自動デプロイ）

## テスト実行（推奨）
- `uv run pytest` でテストを実行（将来的に追加予定）

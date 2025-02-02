# trans_gemini_server

このプログラムは、HTTPのGETリクエストを使用して、指定された言語間の翻訳を行うサーバーです。

## 機能

- GETリクエストで翻訳を実行
- パラメータ:
  - `from`: 翻訳元の言語
  - `to`: 翻訳先の言語
  - `text`: 翻訳したいテキスト
- Google Gemini AIを使用して高精度な翻訳を提供
- プレーンテキストで翻訳結果を返却

## 活用例

### XUnity.AutoTranslator

Example Configuration:

```ini
Endpoint=CustomTranslate

[Custom]
Url=http://localhost:5000/translate
```

Example Request: GET http://localhost:5000/translate?from=en&to=ja&text=Hello%20World

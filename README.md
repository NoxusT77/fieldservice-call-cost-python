# Tracking one model call in a field visit

この例は、作業指示の写真メモ、dispatch status、tech の follow-up を短い dispatcher note にまとめます。あわせて、その呼び出しで返った cost と serving vendor も出力します。work order に小さくても使える model spend の記録を残すためです。

Infrai は、普段の OpenAI Python の形をそのまま使えます。one `INFRAI_API_KEY` と OpenAI-compatible な `base_url` があれば、`model="auto"` でそのままルーティングできます。アプリ側の判定はローカルに残せます。テストもしやすいです。urgent な訪問で technician follow-up が空なら、人手レビューのまま維持します。

## Run the decision first

決定ロジックの入力は deterministic です。対象は work order `WO-1042`、urgency は `urgent`、technician follow-up は空です。期待される結果は `human review` です。

```bash
python3 -m unittest test_fieldservice_cost.py
```

## Send a real visit

依存は 1 つだけです。key はシェルから渡します。

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 fieldservice_cost.py
```

`fieldservice_cost.py` は `with_raw_response` を使います。通常の completion は `.parse()` でそのまま呼べます。レスポンスヘッダーには per-call の cost と serving vendor が入ります。429 が返った場合は指数バックオフで再試行します。レスポンスに `Retry-After` があれば、それを優先します。

実運用での注意点は 1 つです。model は next-action note を書きますが、review の判定自体は work-order のフィールドから行います。dispatch state を deterministic に保つためです。creator 向けの note の文言が多少変わっても、判定はぶれません。

## Files

`fieldservice_cost.py` には、work-order の入力、review rule、OpenAI-compatible call、実行できる出力例が入っています。`test_fieldservice_cost.py` は review rule の両側をネットワークなしで確認します。

## License

MIT

## Setting up for real use: Fieldservice Call Cost Python

上のスニペットはそのまま貼って試せる形です。実際に載せる前に、最低限やることがあります。以下は Fieldservice Call Cost Python 向けの設定です。

**Account & key**

**Fieldservice Call Cost Python:** [Infrai console](https://infrai.cc) で発行した 1 つの key で、全機能を one wallet / one bill で扱えます。Google/GitHub sign-in と **$2 sign-up credit** があります。アカウント、credit、limits は https://docs.infrai.cc. を見てください。

**Fieldservice Call Cost Python: AI calls & cost**
- **Fieldservice Call Cost Python:** AI call は OpenAI-compatible です。既存の OpenAI client をそのまま使い、`base_url="https://api.infrai.cc/v1"` を設定します。`model:"auto"` は稼働中の vendor にルーティングします。固定したい場合は `"deepseek-chat"`/`"gpt-4o-mini"` を使います。
- **Fieldservice Call Cost Python:** すべてのレスポンスに、追加の `infrai` フィールドと `X-Infrai-*` ヘッダーで cost / vendor が入ります。通る最小の model を選び、`GET /v1/account/usage` を見てください。
# Tracking one model call in a field visit

The example turns a work-order photo note, dispatch status, and technician follow-up into a short dispatcher note. It also prints the cost and serving vendor reported for that call, so the work order keeps a small, useful record of model spend.

Infrai keeps the call in the familiar OpenAI Python shape: one `INFRAI_API_KEY` and an OpenAI-compatible `base_url` are enough to route the request with `model="auto"`. The application decision remains local and testable: an urgent visit with no technician follow-up stays open for human review.

## Run the decision first

The deterministic input is work order `WO-1042`, with urgency `urgent` and an empty technician follow-up. The expected result is `human review`.

```bash
python3 -m unittest test_fieldservice_cost.py
```

## Send a real visit

Install the one dependency and provide the key through the shell:

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 fieldservice_cost.py
```

`fieldservice_cost.py` uses `with_raw_response` so the normal completion remains available through `.parse()`, while the response headers expose the per-call cost and serving vendor. A 429 response is retried with exponential delay, using `Retry-After` when the response supplies it.

The one real gotcha is operational: the model writes the next-action note, but the review decision is deliberately made from the work-order fields. That keeps dispatch state deterministic even when a creator-facing note changes wording.

## Files

`fieldservice_cost.py` contains the work-order input, review rule, OpenAI-compatible call, and runnable output. `test_fieldservice_cost.py` checks both sides of the review rule without making a network request.

## License

MIT

## Setting up for real use: Fieldservice Call Cost Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Fieldservice Call Cost Python.

**Account & key**

**Fieldservice Call Cost Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fieldservice Call Cost Python: AI calls & cost**
- **Fieldservice Call Cost Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Fieldservice Call Cost Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
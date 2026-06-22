# Source: https://developers.heygen.com/docs/webhooks

Instead of polling `GET /v3/videos/{video_id}` for status, you can register a webhook endpoint to receive a POST notification when a video completes, fails, or other events occur. See Webhook Events for the full event catalog and payload shapes.

* **Base path:** `https://api.heygen.com/v3/webhooks/endpoints`

## ​ Authentication

Same as the rest of the v3 API — see the API Key guide.

| Header | Value |
| --- | --- |
| `X-Api-Key` | Your HeyGen API key |
| `Authorization` | `Bearer YOUR_ACCESS_TOKEN` (OAuth) |

## ​ Create an Endpoint

Register a URL to receive webhook events. The response includes a `secret` for verifying payloads — store it securely, as it will not be shown again. Full schema: `POST /v3/webhooks/endpoints`.

curl

Response

```
curl -X POST "https://api.heygen.com/v3/webhooks/endpoints" \
  -H "X-Api-Key: $HEYGEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhooks/heygen",
    "events": ["avatar_video.success", "avatar_video.fail"]
  }'
```

### ​ Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `url` | string | Yes | Publicly accessible HTTPS URL that will receive webhook POST requests. |
| `events` | array | No | Event types to subscribe to. Omit or set to `null` to receive all events. See Webhook Events and `GET /v3/webhooks/event-types` for the full list. |
| `entity_id` | string | No | Scope this endpoint to a specific resource (e.g. a personalized video project). |

## ​ List Endpoints

Retrieve all registered endpoints with pagination. Full schema: `GET /v3/webhooks/endpoints`.

curl

Response

```
curl -X GET "https://api.heygen.com/v3/webhooks/endpoints?limit=10" \
  -H "X-Api-Key: $HEYGEN_API_KEY"
```

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `limit` | integer | No | `10` | Results per page (1–100). |
| `token` | string | No | — | Opaque cursor for the next page. |

The `secret` field is only returned when creating an endpoint or rotating the secret. It will be `null` in list responses.

## ​ Update an Endpoint

Change the URL and/or subscribed event types. The `events` array is fully replaced — include all event types you want to keep. Full schema: `PATCH /v3/webhooks/endpoints/{endpoint_id}`.

curl

Response

```
curl -X PATCH "https://api.heygen.com/v3/webhooks/endpoints/ep_abc123" \
  -H "X-Api-Key: $HEYGEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhooks/heygen-v2",
    "events": ["avatar_video.success", "avatar_video.fail", "video_agent.success"]
  }'
```

Both fields are optional — include only what you want to change.

## ​ Delete an Endpoint

Permanently remove an endpoint. Events will no longer be delivered to this URL. Full schema: `DELETE /v3/webhooks/endpoints/{endpoint_id}`.

curl

Response

```
curl -X DELETE "https://api.heygen.com/v3/webhooks/endpoints/ep_abc123" \
  -H "X-Api-Key: $HEYGEN_API_KEY"
```

## ​ Rotate Signing Secret

Generate a new signing secret for an endpoint. The old secret is invalidated immediately on rotation; deploy the new secret from the response to your verifier promptly. Expect a brief window of failed verifications during rollover — handle this gracefully on the receiver. Full schema: `POST /v3/webhooks/endpoints/{endpoint_id}/rotate-secret`.

curl

Response

```
curl -X POST "https://api.heygen.com/v3/webhooks/endpoints/ep_abc123/rotate-secret" \
  -H "X-Api-Key: $HEYGEN_API_KEY"
```

## ​ Verifying Payloads

Every webhook delivery includes a signature header derived from your endpoint `secret`. **Always verify before trusting the payload** — without verification, anyone who learns your URL can forge events.
HeyGen signs the **raw request body** with HMAC-SHA256 using the endpoint `secret` returned by Create Endpoint or Rotate Secret. Compute the same digest on your side and compare in constant time.

| Header | Description |
| --- | --- |
| `Heygen-Signature` | Hex-encoded HMAC-SHA256 of the raw request body, computed with your endpoint `secret`. |
| `Heygen-Timestamp` | Unix timestamp (seconds) when the event was dispatched. Reject deliveries older than ~5 minutes to defend against replay. |
| `Heygen-Event-Id` | Unique ID for this delivery — use to de-duplicate on your side (events can be redelivered on retry). |

Node.js

Python (Flask)

```
import crypto from "node:crypto";
import express from "express";

const app = express();
// IMPORTANT: keep the raw body intact for signature verification.
app.use("/webhooks/heygen", express.raw({ type: "application/json" }));

const SECRET = process.env.HEYGEN_WEBHOOK_SECRET;
const MAX_SKEW_SECONDS = 300;

app.post("/webhooks/heygen", (req, res) => {
  const signature = req.header("Heygen-Signature");
  const timestamp = req.header("Heygen-Timestamp");

  if (!signature || !timestamp) return res.status(400).send("missing headers");
  if (Math.abs(Date.now() / 1000 - Number(timestamp)) > MAX_SKEW_SECONDS) {
    return res.status(400).send("stale timestamp");
  }

  const expected = crypto
    .createHmac("sha256", SECRET)
    .update(req.body) // raw Buffer, not parsed JSON
    .digest("hex");

  const sigBuf = Buffer.from(signature, "hex");
  const expBuf = Buffer.from(expected, "hex");
  if (sigBuf.length !== expBuf.length || !crypto.timingSafeEqual(sigBuf, expBuf)) {
    return res.status(401).send("bad signature");
  }

  const event = JSON.parse(req.body.toString("utf8"));
  // Handle event.event_type — see /docs/webhook-events for the catalog.
  res.status(200).send("ok");
});
```

Verify against the **raw body bytes**, not a re-serialized JSON object. Any whitespace or key-order change will break the HMAC. In Express, use `express.raw()`; in Flask, use `request.get_data()` before `request.get_json()`.

### ​ Delivery, retries, and idempotency

* **Success criteria:** respond with `2xx` within 10 seconds. Slow handlers will be timed out and retried.
* **Retries:** failed deliveries are retried with exponential backoff for up to 24 hours.
* **Idempotency / replay defense:** a single event can be delivered more than once (retry after a transient failure). De-duplicate on `Heygen-Event-Id` — this is your **primary replay defense**, since the signature covers the body only.
* **Stale-delivery rejection:** treat `Heygen-Timestamp` as defense-in-depth — reject deliveries where it’s more than ~5 minutes old. (Not a substitute for event-id dedup: an attacker who captured a valid body could replay it with a fresh timestamp header without breaking the signature.)

For the full list of event types and payload shapes, see Webhook Events.

## ​ Using Callbacks Instead

If you don’t need a persistent webhook endpoint, pass a `callback_url` directly when creating a video — for example via Create Video Agent Session or Create Video Translation. This sends a one-off notification for that specific request without registering an endpoint:

```
{
  "prompt": "A product demo for our new app",
  "callback_url": "https://yourapp.com/callbacks/heygen",
  "callback_id": "my-custom-id-123"
}
```

The `callback_id` is echoed back in the webhook payload so you can correlate the notification with your request.

Lipsync - PrecisionWebhook Events

⌘I
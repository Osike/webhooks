# Africa's Talking Webhooks

A lightweight Flask service that receives and processes webhooks from
[Africa's Talking](https://africastalking.com/). It currently handles
**SMS Delivery Reports**, acknowledging each event quickly and handing the
payload off for background processing, which is the pattern Africa's Talking
recommends for reliable webhook handling.

This project leans heavily on Africa's Talking infrastructure: Africa's Talking
sends the SMS on your behalf, tracks it through the mobile network, and calls
this service back with the delivery outcome. The service itself stays small on
purpose so it can sit in front of whatever storage or queue you use.

## How it works

1. You send an SMS through the Africa's Talking SMS API.
2. The mobile network reports the delivery status back to Africa's Talking.
3. Africa's Talking `POST`s a delivery report to this service at
   `/webhooks/africastalking`.
4. The service logs a safe reference (message `id` and `status`), queues the
   payload for later processing, and immediately returns `200 OK` so Africa's
   Talking stops retrying.

```
Your app ──SMS──▶ Africa's Talking ──▶ Mobile network
                        │
                        ▼  delivery report (POST)
             POST /webhooks/africastalking
                        │
                        ▼
              log → enqueue → 200 OK
```

## Endpoint

### `POST /webhooks/africastalking`

Receives Africa's Talking SMS Delivery Reports. Accepts
`application/x-www-form-urlencoded` (the default from Africa's Talking) and
also falls back to JSON.

Fields Africa's Talking sends in a delivery report include:

| Field           | Description                                                        |
| --------------- | ------------------------------------------------------------------ |
| `id`            | The `messageId` returned when the SMS was sent                     |
| `status`        | `Sent`, `Submitted`, `Buffered`, `Rejected`, `Success` or `Failed` |
| `phoneNumber`   | Recipient number in international format                           |
| `networkCode`   | Code of the recipient's mobile network                             |
| `retryCount`    | Number of times Africa's Talking retried sending the message       |
| `failureReason` | Present only when `status` is `Rejected` or `Failed`               |

Response:

```json
{ "status": "success", "message": "Webhook received" }
```

## Getting started

### Requirements

- Python 3.10+
- Flask 3.x

### Install and run

```bash
git clone https://github.com/Osike/webhooks.git
cd webhooks

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install Flask

python app.py
```

The server starts on `http://localhost:5000` with debug mode on.

### Test locally

Simulate an Africa's Talking delivery report with `curl`:

```bash
curl -X POST http://localhost:5000/webhooks/africastalking \
  -d "id=ATXid_123456" \
  -d "status=Success" \
  -d "phoneNumber=%2B254711XXXYYY" \
  -d "networkCode=63902" \
  -d "retryCount=0"
```

You should see a log line like:

```
INFO:__main__:Received Africa's Talking event. Ref ID: ATXid_123456, Status: Success
INFO:__main__:-> [QUEUE SIMULATION] Storing payload for safe offline processing...
```

## Connecting to Africa's Talking

Africa's Talking needs a public URL to call. For local development, expose
port 5000 with a tunnel such as [ngrok](https://ngrok.com/):

```bash
ngrok http 5000
```

Then, in your [Africa's Talking dashboard](https://account.africastalking.com/):

1. Open your app (use the **Sandbox** app while testing).
2. Go to **SMS → SMS Callback URLs → Delivery Reports**.
3. Set the callback URL to `https://<your-host>/webhooks/africastalking`.

Send a test SMS through the sandbox (the
[Africa's Talking simulator](https://developers.africastalking.com/simulator)
is handy for this) and watch the delivery report arrive in your terminal.

## Project structure

```
.
├── app.py          # Flask app and the Africa's Talking webhook handler
├── .gitignore
└── README.md
```

## Extending it

`enqueue_event_for_background_processing()` in `app.py` is a placeholder. In
production you would replace it with a push to Redis, Celery, AWS SQS, or a
database insert so that the webhook response stays fast regardless of how long
downstream processing takes.

Other Africa's Talking callbacks follow the same shape and can be added as new
routes, for example:

- Incoming SMS (`/webhooks/africastalking/incoming`)
- Voice events
- USSD sessions
- Payment notifications
- Airtime status

## References

- [Africa's Talking SMS Delivery Reports](https://developers.africastalking.com/docs/sms/notifications)
- [Africa's Talking SMS API](https://developers.africastalking.com/docs/sms/overview)
- [Flask documentation](https://flask.palletsprojects.com/)

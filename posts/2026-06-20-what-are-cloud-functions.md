---
title: What are cloud functions? A practical tour with real code
date: 2026-06-20
author: Peter Johnston
tags: cloud functions, serverless, javascript, python, go, aws lambda, google cloud, infrastructure
description: A from-scratch explanation of what cloud functions actually are, the problem they solve, and three real-world examples — an image-resize trigger, a scheduled report, and a webhook handler — written in JavaScript, Python, and Go with line-by-line explanations of what each function does.
---

Every few months someone asks me what I mean when I say a piece of a system "runs
on a cloud function." The phrase has become background noise — *serverless*,
*Lambda*, *functions-as-a-service* — and the noise hides a genuinely simple idea.
This post is the explanation I wish I could just hand people: what a cloud function
*is*, what problem it solves, and three real examples with the code spelled out
line by line.

## The idea, stripped down

Normally, when you want code to run on the internet, you rent a computer. You
configure an operating system, install a runtime, start a long-running process
that listens on a port, and then you keep that process alive forever — paying for
the machine whether anyone uses it at 3pm or 3am.

A **cloud function** inverts that. You hand the provider a single function — a
chunk of code with one entry point — and you say *"run this whenever X happens."*
You never provision a server, never start a process, never think about the
operating system. The provider:

- keeps your code dormant and **costs you nothing while it's idle**,
- **spins up an instance on demand** the instant a trigger fires,
- runs your function, hands back the result, and
- **tears the instance down** (or keeps it warm briefly for the next call).

That's the whole model. It's often called **serverless** — not because there are
no servers, but because *you* never see or manage one. It's also called
**Functions-as-a-Service (FaaS)**. The big implementations are **AWS Lambda**,
**Google Cloud Functions** (and Cloud Run functions), **Azure Functions**, and
**Cloudflare Workers**.

### What makes something a good fit

Cloud functions shine when work is **event-driven** and **bursty**:

- A file lands in storage → resize it.
- A timer fires every morning → email a report.
- A webhook arrives from Stripe or GitHub → react to it.
- An HTTP request hits an endpoint → return some JSON.

They're a poor fit for the opposite shape: long-running jobs, work that needs to
hold state in memory between requests, or constant high-throughput traffic where a
always-on server is cheaper. Two constraints flow from the model and are worth
memorizing:

1. **They're stateless.** Each invocation may run on a fresh instance. Anything you
   want to keep — uploaded files, counters, sessions — lives in an external store
   (a database, object storage, a cache), never in a local variable between calls.
2. **They're short-lived.** Providers cap execution time (commonly a few minutes).
   A function is a sprinter, not a marathon runner.

There's also one famous wrinkle: the **cold start**. If your function hasn't run
recently, the provider has to load the runtime and your code before executing —
adding anywhere from tens of milliseconds to a couple of seconds. Stay "warm" by
being called often, and that overhead disappears.

With the model in place, let's look at real functions. I'll use three languages so
you can see that the *shape* is the same everywhere; only the syntax changes.

## Example 1 — Resize an image when it's uploaded (Python, Google Cloud Functions)

This is the canonical event-driven example. A user uploads a photo to a storage
bucket; we want a thumbnail generated automatically. There's no HTTP request and no
user waiting — the **upload event itself** is the trigger.

```python
# main.py — deployed to Google Cloud Functions (2nd gen), Python runtime.
# Trigger: a "finalize" event on a Cloud Storage bucket (i.e. an object was created).

import io
from PIL import Image          # Pillow: the standard Python imaging library
from google.cloud import storage

# Reuse a single storage client across warm invocations instead of
# reconnecting every time. This is the stateless rule done right:
# the client is a connection helper, not application state.
storage_client = storage.Client()

THUMBNAIL_SIZE = (200, 200)
THUMBNAIL_BUCKET = "my-app-thumbnails"

def make_thumbnail(cloud_event):
    """Triggered whenever a new object is finalized in the watched bucket."""

    # The event payload tells us *which* file triggered us. We never
    # receive the file's bytes directly — only its coordinates.
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    # Guard against infinite loops: if we wrote a thumbnail back into a
    # watched bucket, that write would trigger us again. Skip what we made.
    if file_name.startswith("thumb_"):
        print(f"Skipping already-thumbnailed file: {file_name}")
        return

    # 1. Download the original image's bytes from the source bucket.
    source_bucket = storage_client.bucket(bucket_name)
    blob = source_bucket.blob(file_name)
    image_bytes = blob.download_as_bytes()

    # 2. Resize it in memory. No temp files on disk — the instance is
    #    ephemeral and the local filesystem is throwaway.
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail(THUMBNAIL_SIZE)        # preserves aspect ratio

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)                          # rewind so we can read from the start

    # 3. Upload the result to a *different* bucket (avoids the loop above).
    dest_bucket = storage_client.bucket(THUMBNAIL_BUCKET)
    dest_blob = dest_bucket.blob(f"thumb_{file_name}")
    dest_blob.upload_from_file(buffer, content_type="image/jpeg")

    print(f"Wrote thumb_{file_name} ({image.size}) to {THUMBNAIL_BUCKET}")
```

**What this code does, step by step.** The function `make_thumbnail` is the entry
point — the single piece of code the cloud provider invokes. It receives a
`cloud_event` object describing *what happened*, not the file itself: we get the
bucket name and file name and have to fetch the bytes ourselves. We download the
original, use Pillow's `thumbnail()` to shrink it (which keeps the aspect ratio),
and write the result to a separate thumbnails bucket.

Two details capture the cloud-function mindset:

- **The loop guard.** Writing a file into a bucket can itself fire a "new object"
  event. If we wrote thumbnails back into the *source* bucket, the function would
  trigger itself forever. We avoid it by writing to a different bucket and by
  skipping names that start with `thumb_`. This kind of self-triggering bug is a
  rite of passage in event-driven systems.
- **Everything in memory.** We never touch local disk. The instance might be
  destroyed the moment we return, so we treat its filesystem as scratch space at
  best and do the whole transformation through `io.BytesIO` buffers.

You'd deploy it with a one-liner that wires the bucket event to the function:

```bash
gcloud functions deploy make_thumbnail \
  --gen2 --runtime=python312 --region=us-central1 \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=my-app-uploads" \
  --entry-point=make_thumbnail
```

Notice what's absent: no server, no Dockerfile, no port, no process manager. You
name the trigger and the entry point, and you're done.

## Example 2 — A scheduled daily report (JavaScript, AWS Lambda)

Not every trigger is an event from another service. A very common one is **time**:
"run this every morning at 8am." Here a scheduler (AWS EventBridge) invokes a
Node.js Lambda that tallies yesterday's orders and emails a summary.

```javascript
// index.mjs — AWS Lambda, Node.js runtime.
// Trigger: an EventBridge schedule rule, e.g. cron(0 8 * * ? *) = 08:00 UTC daily.

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { QueryCommand } from "@aws-sdk/lib-dynamodb";
import { SESClient, SendEmailCommand } from "@aws-sdk/client-ses";

// Clients declared OUTSIDE the handler. On a warm start the module is
// already loaded, so these are reused — a cheap, important optimization.
const db = new DynamoDBClient({});
const ses = new SESClient({});

// The handler is the entry point AWS calls. `event` carries trigger
// metadata; for a scheduled rule we mostly ignore it.
export const handler = async (event) => {
  // 1. Figure out "yesterday" as an ISO date string (YYYY-MM-DD).
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 10);

  // 2. Query the orders table for everything created yesterday.
  const result = await db.send(
    new QueryCommand({
      TableName: "Orders",
      IndexName: "byDate",
      KeyConditionExpression: "orderDate = :d",
      ExpressionAttributeValues: { ":d": yesterday },
    })
  );

  const orders = result.Items ?? [];
  const revenue = orders.reduce((sum, o) => sum + Number(o.total), 0);

  // 3. Compose and send the summary email via SES.
  await ses.send(
    new SendEmailCommand({
      Source: "reports@example.com",
      Destination: { ToAddresses: ["owner@example.com"] },
      Message: {
        Subject: { Data: `Daily report for ${yesterday}` },
        Body: {
          Text: {
            Data:
              `Orders: ${orders.length}\n` +
              `Revenue: $${revenue.toFixed(2)}`,
          },
        },
      },
    })
  );

  // 4. Return a value. Nobody is "waiting" on an HTTP response here,
  //    but the return is logged and signals success to the platform.
  return { statusCode: 200, ordersProcessed: orders.length };
};
```

**What this code does.** `handler` is the function AWS Lambda runs on a schedule.
It computes yesterday's date, queries a DynamoDB table for that day's orders, sums
the revenue, and emails a two-line summary through SES (Simple Email Service). Then
it returns a small object — there's no browser on the other end, but the return
value is logged and tells Lambda the run succeeded.

The thing to internalize here is that **the function doesn't know or care what
triggered it**. The exact same handler could be wired to an HTTP endpoint, a queue
message, or this cron schedule. The trigger is configured *around* the function, in
the platform, not baked into the code. That separation is the heart of the FaaS
model: your code is a pure unit of work, and the platform decides when to run it.

Again, the clients live outside `handler` deliberately. On a **cold start** the
whole module loads and the clients are constructed; on subsequent **warm starts**
the module is still in memory, so only `handler` runs and the connections are
reused. Putting them inside the handler would needlessly rebuild them every call.

## Example 3 — A webhook handler (Go, any HTTP-triggered platform)

The third classic trigger is a plain **HTTP request** — often a *webhook*, where
another service calls *you* to announce something happened. Here, GitHub pings us
on every push. The function verifies the request is genuinely from GitHub, then
acts on it.

```go
// function.go — an HTTP-triggered function (Google Cloud Functions / Cloud Run).
package webhook

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

// pushPayload is the slice of GitHub's JSON we actually care about.
type pushPayload struct {
	Ref        string `json:"ref"`
	Repository struct {
		FullName string `json:"full_name"`
	} `json:"repository"`
}

// HandlePush is the entry point. Its signature is just Go's standard
// http.HandlerFunc — the platform routes incoming requests to it.
func HandlePush(w http.ResponseWriter, r *http.Request) {
	// 1. Read the raw body once. We need the exact bytes both to verify
	//    the signature and to parse the JSON.
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "cannot read body", http.StatusBadRequest)
		return
	}

	// 2. Verify the payload really came from GitHub. GitHub signs each
	//    request with a shared secret using HMAC-SHA256. We recompute the
	//    signature and compare — never trust an unverified webhook.
	if !validSignature(body, r.Header.Get("X-Hub-Signature-256")) {
		http.Error(w, "bad signature", http.StatusUnauthorized)
		return
	}

	// 3. Parse just the fields we want out of the JSON body.
	var payload pushPayload
	if err := json.Unmarshal(body, &payload); err != nil {
		http.Error(w, "bad json", http.StatusBadRequest)
		return
	}

	// 4. Do the actual work. Here we just log it; in real life you might
	//    kick off a deploy, post to Slack, or enqueue a build.
	fmt.Printf("Push to %s on %s\n", payload.Repository.FullName, payload.Ref)

	// 5. Respond fast. Webhook senders expect a quick 2xx; slow handlers
	//    get retried or marked as failed.
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "ok")
}

// validSignature recomputes GitHub's HMAC-SHA256 over the body and
// compares it to the header in constant time (hmac.Equal avoids leaking
// timing information about where the comparison failed).
func validSignature(body []byte, header string) bool {
	secret := os.Getenv("GITHUB_WEBHOOK_SECRET")
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(body)
	expected := "sha256=" + hex.EncodeToString(mac.Sum(nil))
	return hmac.Equal([]byte(expected), []byte(header))
}
```

**What this code does.** `HandlePush` is an ordinary Go HTTP handler, and that's
exactly the point — the cloud platform takes incoming HTTPS requests and routes
them to this function, so you write it the same way you'd write any Go web handler.
It reads the request body, **verifies the cryptographic signature** so we know the
request truly came from GitHub and not an imposter, parses out the repository name
and branch ref, logs the event, and returns `200 OK` quickly.

Two real-world lessons are baked in:

- **Always verify webhooks.** Your function's URL is effectively public. Anyone who
  learns it can POST fake events. GitHub (like Stripe, Slack, and others) signs
  each request with a shared secret; `validSignature` recomputes that HMAC and uses
  `hmac.Equal` for a constant-time comparison, which avoids leaking — through
  response timing — how much of the signature matched.
- **Respond fast.** Webhook providers expect a prompt `2xx`. If the real work is
  slow (a full deploy, a video transcode), the right pattern is to acknowledge
  immediately and hand the heavy lifting to a queue or another function, rather
  than making GitHub wait.

## The pattern underneath all three

Look back at the examples and the family resemblance is obvious. In every case you
wrote **one function with a single entry point**, and something *external* — a file
upload, a clock, an HTTP request — decided when it ran:

| Example | Language | Trigger | Entry point |
|---|---|---|---|
| Thumbnailer | Python | Storage upload event | `make_thumbnail` |
| Daily report | JavaScript | Scheduled timer | `handler` |
| Webhook | Go | HTTP request | `HandlePush` |

None of them provisioned a server, opened a port, or ran a loop waiting for work.
None of them stored anything in a local variable expecting it to survive to the
next call. Each was small, single-purpose, and stateless — and each one costs
nothing when no one is using it.

That's the deal cloud functions offer: give up persistent in-memory state and
long-running processes, and in exchange you stop thinking about servers entirely.
You write the *what* — the unit of work — and the platform owns the *when* and the
*where*. For event-driven, bursty, glue-the-services-together work, it's hard to
beat. And once the model clicks, you start seeing functions everywhere a system
says *"when X happens, do Y."*

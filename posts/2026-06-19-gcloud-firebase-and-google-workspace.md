---
title: gcloud, Firebase, and why I keep paying for a Workspace account
date: 2026-06-19
author: Peter Johnston
tags: google cloud, firebase, gcloud, google workspace, infrastructure, serverless, apps script
description: A working tour of Google Cloud and Firebase — what each one actually is, where the line between them sits, how they integrate through a shared project and IAM, and why a paid Google Workspace account ends up being the quiet keystone that ties it all together.
---

I keep ending up inside Google's ecosystem. Not because I set out to be a Google
shop — most of what I build is small, nonprofit-adjacent, and allergic to monthly
bills — but because every time I reach for a piece of infrastructure, the Google
option is already half-configured by the time I've finished reading the docs for
the alternative. This post is an attempt to write down, in one place, the mental
model I've built up: what **Google Cloud** is, what **Firebase** is, how the two
fit together, and why the thing that quietly makes all of it pleasant is having a
real **Google Workspace** account instead of a free Gmail address.

I'll keep this practical. The goal isn't a feature list — Google has plenty of
those — it's the shape of the thing, the parts that confused me at first, and the
handful of decisions that matter.

## The one-sentence version

Google Cloud Platform (GCP) is the full industrial-grade cloud — compute,
storage, networking, databases, machine learning, the works — operated through
the `gcloud` CLI and the Cloud Console. Firebase is a friendlier product surface
built *on top of the same infrastructure*, aimed at people shipping apps who don't
want to think about servers. They are not two clouds. They are two front doors to
one cloud, and a Firebase project **is** a Google Cloud project wearing a nicer
jacket.

That last sentence is the whole insight. Everything else is detail.

## What "gcloud" actually refers to

People say "gcloud" to mean three different things, and it's worth pulling them
apart because the confusion costs you time:

- **Google Cloud Platform** — the platform itself: the regions, the services, the
  billing account, the IAM model.
- **`gcloud`** — the command-line tool, part of the Google Cloud CLI (formerly
  the "Cloud SDK"). This is what you actually type. `gcloud`, `gsutil` (for
  Cloud Storage), and `bq` (for BigQuery) ship together.
- **The Cloud Console** — the web UI at `console.cloud.google.com`, which is just
  a graphical front-end over the same APIs the CLI hits.

The unit you organize everything around is the **project**. A project is a billing
and permissions boundary: every resource lives in exactly one project, every API
is enabled or disabled per project, and every IAM grant is scoped to a project (or
to a folder/organization above it). When you start a new thing, you make a new
project. When you're confused about why something doesn't have access to something
else, the answer is almost always "they're in different projects" or "the API
isn't enabled."

A minimal first session looks like this:

```bash
# Authenticate the CLI with your Google identity
gcloud auth login

# Create a project (the ID must be globally unique)
gcloud projects create my-thing-2026 --name="My Thing"

# Point the CLI at it so you stop typing --project everywhere
gcloud config set project my-thing-2026

# Link a billing account (required before most APIs will run)
gcloud billing projects link my-thing-2026 --billing-account=XXXXXX-XXXXXX-XXXXXX

# Turn on the APIs you actually need
gcloud services enable run.googleapis.com firestore.googleapis.com
```

The thing that trips up newcomers: **APIs are off by default.** Every service —
Cloud Run, Firestore, the Vision API, everything — has to be explicitly enabled on
the project before it'll answer. This is a feature, not a bug; it keeps the attack
surface and the bill small. But the first error you hit on any new service is
usually "API not enabled," and now you know the fix.

### The pieces of GCP worth knowing about

You do not need to learn all 200-odd services. The ones I reach for, roughly in
order of how often:

- **Cloud Run** — run a container (or just a web server) and have it scale to zero
  when nobody's using it. You pay per request, not per hour. For small projects
  this is close to free, and it's my default for anything that needs a backend.
- **Cloud Storage** — object storage (buckets and blobs), the place static files,
  backups, and data dumps live. Accessed via `gsutil` or the client libraries.
- **Firestore** — a serverless NoSQL document database. (Hold this thought; it's
  the main bridge to Firebase.)
- **BigQuery** — a serverless data warehouse that will chew through terabytes with
  SQL and bill you by bytes scanned. Wildly good for analytics; I've used it to
  grind through bulk IRS Form 990 data.
- **Cloud Functions** — single-purpose functions triggered by an event (an HTTP
  request, a file upload, a database write). The "glue code" of the cloud.
- **IAM** — not a service you "use" so much as the permission fabric underneath
  everything. More on this below, because it's where Firebase and GCP truly meet.

## What Firebase actually is

Firebase started life as an independent startup (a realtime database, originally),
Google acquired it in 2014, and over the following decade it grew into the
app-developer's front end to Google Cloud. The pitch is "backend-as-a-service":
you get authentication, a database, file storage, hosting, and push notifications
without standing up or maintaining a single server.

The headline products:

- **Firebase Authentication** — drop-in sign-in with email/password, Google,
  Apple, GitHub, phone number, and more. This alone is worth the price of
  admission; auth is the thing nobody wants to build from scratch and get wrong.
- **Cloud Firestore** (and the older **Realtime Database**) — the same Firestore
  that lives in GCP, but with client SDKs that sync in real time and offline, and
  a security-rules language that lets the *browser* talk to the database directly
  without a backend in between.
- **Firebase Hosting** — fast static and dynamic hosting with a global CDN, free
  TLS, and atomic deploys. `firebase deploy` and you're live.
- **Cloud Storage for Firebase** — the same Cloud Storage buckets, exposed to
  client apps with their own security rules.
- **Cloud Functions for Firebase** — the same Cloud Functions, wired to Firebase
  events and deployable from the Firebase CLI.
- **Crashlytics, Analytics, Remote Config, App Distribution** — the operational
  layer: crash reporting, usage analytics, feature flags, beta builds.

The tooling is the `firebase` CLI (installed via npm), which is the spiritual
sibling of `gcloud` — same idea, app-developer ergonomics.

## How they integrate — the part that finally made it click

For a long time I treated Firebase and GCP as two separate accounts I happened to
have. They are not. Here is the actual relationship:

**1. A Firebase project is a Google Cloud project.** When you create a project in
the Firebase console, it creates (or adopts) a GCP project with the same ID. Open
the Cloud Console and it's right there. Add Firebase to an existing GCP project and
it works the other way around. There is one project, two consoles.

**2. The databases are literally the same database.** Cloud Firestore in the
Firebase console and Firestore in the Cloud Console are one product. A document you
write from the Firebase web SDK is queryable from a Python script using the Google
Cloud client library, because it's the same Firestore instance in the same project.
This is the single most useful fact in this whole post: **the client app and the
backend share one source of truth, with no sync layer to build.**

**3. The storage buckets are the same buckets.** "Cloud Storage for Firebase" is a
default bucket in your GCP project. Upload from a phone app through the Firebase SDK;
process it from a Cloud Function or a `gsutil` command. Same bytes.

**4. Functions are the same functions.** "Cloud Functions for Firebase" deploy to
GCP's Cloud Functions. The Firebase CLI just gives you a nicer way to write and
deploy them with Firebase triggers attached.

**5. IAM is the shared spine.** This is the deep integration. Both worlds use the
same Identity and Access Management system. When Firebase Auth issues a user a
token, that token is verifiable by GCP services. **Service accounts** — the
non-human identities your code runs as — are GCP service accounts, and you grant
them roles with `gcloud`. Firestore Security Rules (the browser-facing layer) and
IAM (the server-facing layer) are two enforcement points over one permission model.

The mental model I settled on: **Firebase is the client-facing skin; GCP is the
server-facing machine room; IAM is the wall between them with the doors in it.**
A typical app lets the browser talk directly to Firestore and Storage, gated by
Security Rules, for the easy 80%. The hard 20% — anything that needs secrets,
heavy compute, or trust you can't put in a client — runs on Cloud Run or Cloud
Functions as a service account, talking to the *same* Firestore and Storage from
the privileged side.

### A concrete shape

Picture a small app — say, a tool that lets volunteers look up a nonprofit's
filing history:

- The front-end is plain HTML/JS on **Firebase Hosting**.
- Users sign in with **Firebase Auth** (Google sign-in, one button).
- The browser reads public data straight from **Firestore**, gated by Security
  Rules that say "anyone may read, nobody may write."
- A nightly **Cloud Function** pulls fresh data from an external API, processes it,
  and writes it into that same Firestore — running as a service account with write
  permission the browser will never have.
- Big historical crunching happens in **BigQuery**, with results exported back to
  Firestore for the app to serve.

Every one of those pieces is in one project, billed to one account, governed by one
IAM policy. You move between the `firebase` CLI and the `gcloud` CLI depending on
which door is closer to what you're touching, and nothing is duplicated.

## So where does Google Workspace come in?

Here's the part people skip, and it's the reason I keep paying.

You *can* run all of the above with a free `@gmail.com` account. It works. But the
moment a project becomes more than a toy — a custom domain, more than one person,
anything you'd be embarrassed to lose — a personal Gmail account starts showing its
seams. **Google Workspace** (the paid, custom-domain identity product, formerly
G Suite) is what closes them.

What it actually buys you, in cloud terms:

- **A real identity on your own domain.** `peter@mydomain.org` instead of a
  personal Gmail. Your Cloud and Firebase resources are owned by an identity you
  control administratively, not one tied to your personal life. When auth, email,
  and cloud ownership all sit on the same domain, a lot of friction disappears.
- **A Cloud Organization node.** Workspace (or its free sibling, Cloud Identity)
  gives you an **organization** resource at the top of the GCP hierarchy. Without
  it, projects float around loose, owned by individual logins. With it, you get
  folders, org-wide IAM policies, centralized billing, and the ability to set
  guardrails (org policies) that apply to every project underneath. This is the
  difference between "some projects I made" and "an estate I administer."
- **Admin control and continuity.** As a Workspace admin you can suspend or
  transfer accounts, recover data, and reassign ownership. If the one person who
  owned a critical project leaves — or loses their phone — you are not locked out.
  For anything other than a solo hobby, this is the whole ballgame.
- **The productivity suite that your cloud code talks to.** Gmail, Drive, Docs,
  Sheets, Calendar — and crucially their **APIs** and **Apps Script**. I've built
  more than one useful thing as an Apps Script bound to a Google Sheet, calling
  external APIs and writing results back into the sheet. Workspace makes those
  scripts run under a managed domain identity with proper sharing controls, and it
  raises the quotas and removes the "unverified app" friction that personal
  accounts hit. The line between "a spreadsheet" and "a small application" gets
  very blurry, in a good way.
- **Domain-verified email and OAuth.** Sending mail from your domain, verifying
  ownership for OAuth consent screens, custom Firebase Auth email templates that
  come from *your* address — all smoother when the domain is one you administer
  through Workspace.

The honest framing: Workspace doesn't unlock a cloud feature you couldn't
otherwise reach. What it does is give you a **stable, administrable, domain-rooted
identity** to hang everything off of — Cloud, Firebase, email, documents,
automation — so that the whole estate has one owner, one billing relationship, and
one place to set policy. For a few dollars a month, it turns a pile of
personally-owned logins into something that looks and behaves like an organization.
That's worth it the moment anything you build matters.

## The decision, compressed

If you're starting out and just want to learn: a free Gmail account, the `gcloud`
and `firebase` CLIs, and Cloud Run's scale-to-zero will take you remarkably far for
remarkably little money.

The moment you have a custom domain, a collaborator, or a project you'd grieve to
lose, get a Workspace account (or at minimum Cloud Identity) and create a real
organization node. Do it *before* you have ten projects scattered across a personal
login, because retrofitting an org around existing projects is a chore and starting
clean is free.

And keep the core insight close: it's one cloud, two front doors. Once you stop
thinking of Firebase and Google Cloud as separate things and start thinking of them
as the client side and the server side of a single project — with IAM as the wall
between them and a Workspace identity as the deed to the whole property — the
ecosystem stops feeling sprawling and starts feeling like one tool.

*(Draft — corrections and disagreements welcome.)*

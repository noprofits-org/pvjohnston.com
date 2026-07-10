---
title: The Met API has no random button
date: 2026-06-18
author: Peter Johnston
tags: art, javascript, react, met museum, cors proxy, randomness, pwa
description: A year ago I shipped a one-button "random artwork" toy on top of the Met Museum API. It has since grown into a four-screen app — and the interesting part is what you do when the API you're randomizing over has no way to hand you something random. Manufacture it. And once you can manufacture randomness, a deterministic "artwork of the day" falls out for free.
---

A little over a year ago I wrote up a small toy: the [Met Random Art
Generator](/posts/random-art-generator.html), a single button that pulled a random
piece from the [Metropolitan Museum of Art's open API](https://metmuseum.github.io/)
and put it on screen. The whole point of that post was the [serverless CORS
proxy](/posts/cors-proxy.html) sitting behind it — the art generator was just the
demo that proved the proxy worked.

The demo outlived its purpose. Over the past year it grew into an actual app —
now living at [rag.noprofits.org](https://rag.noprofits.org) — with four screens, a
swipeable card stack, a favorites collection, and a daily artwork. This post is
about the two decisions that shaped it: how you fake randomness over an API that
won't give you any, and how, once you can fake it, you get a deterministic
"artwork of the day" for nothing.

## The problem: there is no random object

The Met's API is generous — no key, no rate limit to speak of, ~half a million
objects — but it has no endpoint that means *give me a random artwork*. What it has
is:

- `/objects` — every object ID, all ~500k of them, as one giant array.
- `/objects/{id}` — the full record for one object.
- `/search?q=...` — IDs matching a text query, optionally filtered.

The naive move — the one the original toy made — is to grab the full ID list and
pick an index with `Math.random()`. It technically works, and it's technically
random. But most of those IDs have no image, or no rights to show one, so you spend
most of your clicks fetching a record only to discover there's nothing to display.
A "random art generator" that shows you a blank card half the time is not a random
art generator.

The fix is to stop randomizing over *all objects* and start randomizing over *all
objects that have an image*. The search endpoint can do exactly that filter —
`hasImages=true` — but search needs a query. You can't search for "anything." So
you search for something common enough to return a deep pool, and you rotate what
that something is:

```js
const SEED_TERMS = [
  'portrait', 'landscape', 'flowers', 'figure', 'study', 'river', 'garden',
  'still life', 'horse', 'temple', 'goddess', 'vessel', 'mask', 'textile',
  'drawing', 'sculpture', 'ship', 'king', 'queen', 'dancer', 'tree', 'moon',
  'gold', 'silver', 'blue', 'red', 'green', 'ivory', 'bronze', 'marble',
  // ...
];

async function fetchPool({ departmentId = null, term = null } = {}) {
  const q = term || pick(SEED_TERMS);
  let url = MET_BASE + '/search?hasImages=true&q=' + encodeURIComponent(q);
  if (departmentId) url += '&departmentId=' + departmentId;
  const data = await fetchJSON(url);
  return shuffle(data.objectIDs || []);   // local Fisher–Yates
}
```

Each seed term — "horse," "marble," "moon" — returns hundreds or thousands of IDs,
*every one of which has an image*, because the API guaranteed it. Rotating the term
across a session gives you breadth the way a true random walk over 500k objects
never could, and it does it while sidestepping the blank-card problem entirely. The
randomness is real — `shuffle` is a Fisher–Yates over the returned IDs — it's just
been fenced into a region of the collection that's worth looking at.

## A self-refilling buffer, not a button

The original was strictly one-shot: click, fetch, wait, look. A swipeable stack
needs the *next* card ready before you ask for it, and it needs to quietly skip the
occasional dud (an ID whose image 404s, or whose record came back without a usable
thumbnail). So the pool got wrapped in a small feed object that refills itself:

```js
function createFeed({ departmentId = null, term = null } = {}) {
  let pool = [], cursor = 0, scope = { departmentId, term };

  async function ensurePool() {
    if (cursor >= pool.length) { pool = await fetchPool(scope); cursor = 0; }
  }

  async function next() {
    let tries = 0;
    while (tries < 24) {
      tries++;
      await ensurePool();              // refetch + reshuffle when drained
      const id = pool[cursor++];
      if (id == null) continue;
      try {
        const art = await fetchObject(id);
        if (art && art.thumb) return art;   // skip anything unshowable
      } catch (e) { /* skip */ }
    }
    throw new Error('Could not load artwork');
  }

  return { next, setScope };
}
```

`next()` is the whole UX in one function: walk the shuffled pool, fetch records,
skip anything without a thumbnail, refetch a fresh pool when the current one runs
dry, and give up gracefully after 24 misses rather than spinning forever. The card
stack just calls `next()` whenever it needs another card and preloads the image
before flipping it into view.

## The payoff: a daily artwork for free

Here's the part I like. Once randomness is "pick an index into a pool," *determinism
is the same machine with the dice swapped out.* The "Today" screen shows everyone
the same artwork on the same calendar day, with no server deciding what that is —
because the date itself is the seed:

```js
function dailySeed() {
  const t = todayKey();                       // "2026-06-18"
  let h = 0;
  for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) >>> 0;
  return h;                                   // same date → same integer, everywhere
}
```

That's the classic string hash (`h = 31·h + c`) over the date string. Feed its
output where `Math.random()` used to go, and the selection becomes a pure function
of the day:

```js
const seed = Store.dailySeed();
const term = DAILY_TERMS[seed % DAILY_TERMS.length];   // deterministic term
const pool = await MetAPI.fetchPool({ term });
for (let k = 0; k < pool.length; k++) {
  const idx = (seed + k * 7) % pool.length;            // deterministic walk
  const id = pool[idx];
  const art = await MetAPI.fetchObject(id).catch(() => null);
  if (art && art.thumb) return art;                    // first showable wins
}
```

Two visitors on opposite sides of the world, both opening the app on June 18, get
the same "Artwork of the Day" — no database, no cron job, no shared state. The only
coordination is the calendar. The result is cached in `localStorage` so a second
visit the same day doesn't re-walk the pool, and a tiny visit-streak counter rides
along beside it. The whole feature is a few dozen lines, and it exists purely
because the randomness was already factored into "seed → index."

## Still no build step

One thing I was stubborn about: this is React now — four screens, routing, a detail
overlay with a zoom/pan lightbox — but it still has **no build step**. The `.jsx`
files are transpiled in the browser by Babel Standalone:

```html
<script src="https://unpkg.com/react@18.3.1/umd/react.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js"></script>
<script type="text/babel" src="js/met.jsx"></script>
<script type="text/babel" src="js/app.jsx"></script>
```

It deploys to GitHub Pages exactly like a plain HTML page — `git push` and you're
done. No npm, no bundler, no CI step, no `node_modules` to rot. For a personal
project I touch every few weeks, that tradeoff is the right one: I'd rather pay a
little transpile-on-load cost in the client than maintain a toolchain between me and
a one-line fix. It is emphatically *not* the right call for anything with real
traffic — you ship the entire Babel compiler to every visitor and recompile on
every load — and the honest cost shows up in one sharp edge: you can't open
`index.html` from `file://`, because the browser blocks Babel from fetching the
`.jsx` files over the `file:` protocol. You have to serve it over `http://` even
locally. Worth knowing before you copy the pattern.

## The proxy, a year on

The CORS proxy that started the whole thing is still in the loop, but it's no longer
the *only* thing in the loop. The API service tries direct, then the proxy, then a
public fallback, in order:

```js
const PROXY_WRAPS = [
  (u) => u,                                                              // direct
  (u) => 'https://cors-proxy-xi-ten.vercel.app/api/proxy?url=' + encodeURIComponent(u),
  (u) => 'https://corsproxy.io/?' + encodeURIComponent(u),              // fallback
];
```

The Met's API actually sends permissive CORS headers for most requests, so the
direct path usually wins and the proxy only catches the cases that don't. That's a
nice inversion from the original post, where the proxy was load-bearing. It's also
why [hardening that proxy](/posts/2026-06-15-hardening-the-cors-proxy.html) mattered: it now
runs an allowlist, and `rag.noprofits.org` is on it, so the app's own traffic sails
through while the open-relay door I'd left ajar is shut.

## What I left undone

Two honest notes. The detail view has a *Curator's Note* — a short AI-written
paragraph about the piece — that only works inside Claude's design environment,
where `window.claude.complete` exists. On the live site it degrades to a polite
"not available right now." Wiring it to a real model endpoint is future work I
haven't done.

And I kept the old version. The previous single-file app is still there at
[`classic.html`](https://rag.noprofits.org/classic.html), powered by the original
`main.js`, so the thing that post a year ago described still runs, side by side with
what it became. Partly that's sentiment. Mostly it's that "the old one still works"
is a feature, and deleting working code to feel tidy is a bad trade.

If you want to poke at it: [rag.noprofits.org](https://rag.noprofits.org), source on
[GitHub](https://github.com/noprofits-org/random-art-generator). Swipe right on the
ones you like.

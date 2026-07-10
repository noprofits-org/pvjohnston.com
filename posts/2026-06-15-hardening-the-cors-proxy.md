---
title: Hardening the open CORS proxy — allowlists, SSRF guards, and the bypass I almost left behind
date: 2026-06-15
author: Peter Johnston
tags: cors proxy, serverless, vercel, security, ssrf, javascript, tikz
description: A year after building an open serverless CORS proxy, I closed the open-relay hole it had become — target and origin allowlists, SSRF guards, a resilience layer — and learned a sharp lesson about a forgotten debug endpoint that Vercel was still routing.
---

A little over a year ago I wrote up a [serverless CORS proxy on
Vercel](/posts/cors-proxy.html) — a single function that takes `?url=<target>`,
fetches it server-side, and hands the response back to the browser with the CORS
headers the upstream API never sent. It solved a real, recurring problem across my
nonprofit side projects, and that post ended on an honest caveat:

> The proxy is currently open without authentication, making it accessible to
> anyone. For production applications... deploying a private instance with
> additional security measures is recommended.

That throwaway line was the whole story. "Open without authentication" is a polite
way of saying **open relay**: the proxy would forward *any* `?url=` to *any* host
and stamp `Access-Control-Allow-Origin: *` on the way back. This post is how I
closed that hole — and the diagram below is the data flow I ended up with.

## What "open" actually meant

Two properties made the original proxy a liability, not just a convenience:

- **Any target.** `?url=https://anything` was forwarded verbatim. That turns the
  proxy into an anonymizing relay for whoever finds it, and — worse — into an
  **SSRF** vector: a request for `http://169.254.169.254/…` (the cloud
  metadata endpoint) or `http://10.0.0.5/…` (an internal host) is made *from
  Vercel's network*, not the attacker's. The proxy was a confused deputy.
- **`ACAO: *` unconditionally.** Every response advertised that *any* web origin
  could read it. The `ALLOWED_ORIGINS` env var I'd documented in the README was
  never actually read by the code.

None of this was hypothetical. When I later pulled the production runtime logs, a
scanner was already hammering `?url=<random host>` looking for exactly this kind
of open relay.

## The shape I wanted

Before touching code I drew the target: a request should pass a short stack of
**gates** before any upstream fetch happens, each able to reject early, and the
response should carry a *scoped* CORS header — the matched origin, never `*`. Every
figure on this blog is compiled from TikZ at build time, so the diagram below is
the actual source, not a screenshot:

```tikzpicture
\begin{tikzpicture}[
  font=\small,
  >={Stealth[length=2.4mm]},
  box/.style={draw, rounded corners=2pt, align=center,
              minimum height=11mm, minimum width=20mm, thick},
  gate/.style={box, fill=blue!8, draw=blue!55!black},
  endpoint/.style={box, fill=black!7, draw=black!55, minimum width=26mm},
  cache/.style={box, fill=green!10, draw=green!55!black},
  flow/.style={->, thick, black!75},
  ret/.style={->, thick, green!55!black},
  reject/.style={->, thick, red!70!black, dashed},
  sub/.style={font=\scriptsize},
  rj/.style={align=center, font=\footnotesize\bfseries, red!72!black},
]
  % ---- main pipeline (left -> right) ----
  \node[endpoint] (br) at (0,0)    {Browser\\[-1pt]{\scriptsize grants.noprofits.org}};
  \node[gate]     (g1) at (3.8,0)  {Origin\\allowlist};
  \node[gate]     (g2) at (7.6,0)  {Target allowlist\\+ SSRF guard};
  \node[gate]     (g3) at (11.4,0) {Rate limit\\{\scriptsize 60/min\,$\cdot$\,IP}};
  \node[cache]    (g4) at (14.8,0) {Cache\\{\scriptsize LRU\,+\,TTL}};
  \node[endpoint] (up) at (19.4,0)
        {Upstream API\\[-1pt]{\scriptsize projects.propublica.org}\\[-2pt]{\scriptsize collectionapi.metmuseum.org}};

  % forward flow
  \draw[flow] (br) -- node[above,sub]{\texttt{?url=}} (g1);
  \draw[flow] (g1) -- (g2);
  \draw[flow] (g2) -- (g3);
  \draw[flow] (g3) -- (g4);
  \draw[flow] (g4) -- node[below,sub,align=center]{\texttt{resilientFetch}\\[-1pt]timeout\,+\,retry} (up);

  % response return (top rail)
  \draw[ret] (up.north) -- ++(0,1.2)
        -| node[above,pos=0.22,sub]{response \,$\cdot$\, \texttt{ACAO: matched origin} (never \texttt{*})} (br.north);

  % ---- rejection rail (below the gates) ----
  \node[rj] (rj1) at (3.8,-2.45)  {403\\{\scriptsize\mdseries bad origin}};
  \node[rj] (rj2) at (7.6,-2.45)  {403\\{\scriptsize\mdseries bad target / SSRF}};
  \node[rj] (rj3) at (11.4,-2.45) {429\\{\scriptsize\mdseries rate limited}};
  \draw[reject] (g1.south) -- (rj1);
  \draw[reject] (g2.south) -- (rj2);
  \draw[reject] (g3.south) -- (rj3);

  % cache HIT short-circuit (green dashed, back to browser)
  \draw[ret, dashed] (g4.south) |- (0,-1.25)
        node[below,pos=0.78,sub]{cache \texttt{HIT} $\rightarrow$ cached body} -- (br.south);

  % ---- removed open-relay bypass (the #6 cleanup) ----
  \draw[dashed, red!40, line width=1pt] (br.south) |- (9.7,-3.95) -| (up.south);
  \node[fill=white, draw=red!55!black, rounded corners=2pt, text=red!65!black,
        font=\scriptsize, inner sep=3pt, align=center] at (9.7,-3.95)
        {\texttt{/api/debug-proxy.js} --- old unguarded open relay, \textbf{removed (\#6)}};
  \node[red!75!black, font=\normalsize\bfseries] at (4.55,-3.95) {$\times$};
  \node[red!75!black, font=\normalsize\bfseries] at (14.85,-3.95) {$\times$};
\end{tikzpicture}
```

Read it left to right: a browser request enters, passes the origin and target
gates, the rate limiter, and the cache, and only then reaches `resilientFetch`,
which talks to the one or two upstreams the proxy is actually for. A failed gate
drops straight down to a `403`/`429` instead of leaking a generic `500`. The
greyed-out path along the bottom is the part I almost missed — more on that below.

## Layer 1 — the lockdown (allowlists + SSRF guard)

The first change made the proxy *closed by default*:

- **Target allowlist.** `ALLOWED_TARGETS` defaults to exactly the two hosts my
  apps proxy — `projects.propublica.org` (the IRS-990 / Nonprofit Explorer API)
  and `collectionapi.metmuseum.org` (the Met's collection API). Anything else gets
  a clean `403 Target host is not allowed`, not a fetch.
- **Origin allowlist.** `ALLOWED_ORIGINS` defaults to `noprofits.org` and its
  subdomains (plus `localhost` for dev), and the response now **echoes the matched
  origin** rather than `*`. The env var the old README promised is finally wired
  in.
- **HTTPS-only + an always-on SSRF guard** that blocks `localhost`, RFC-1918
  private ranges, link-local, and the cloud-metadata addresses *even if* someone
  overrides the target allowlist. Defense that an env var can't switch off.

Setting `ALLOWED_TARGETS=*` / `ALLOWED_ORIGINS=*` restores the old open-relay
behavior for anyone who forks it and actually wants a general proxy — but you have
to opt into that now, loudly.

## Layer 2 — resilience

With the security boundary in place I added the reliability layer the diagram's
last two boxes represent, because a proxy that's a single point of failure for
several apps should fail gracefully:

- **`resilientFetch`** — a per-attempt timeout (an `AbortController` at 8 s) with
  retry and exponential backoff + jitter for network blips, `429`s, and `5xx`s,
  all bounded by a 9 s overall budget that stays under Vercel's 10 s function
  limit. `4xx`s are never retried; a `429` with a small `Retry-After` is honored.
  Timeouts surface as a `504` and other upstream failures as a `502`, instead of a
  misleading `500`.
- **An LRU + TTL cache** for deterministic `2xx` GETs, tagged with
  `X-Proxy-Cache: HIT|MISS`. That's the green short-circuit in the diagram — a hit
  never touches the upstream.
- **A fixed-window per-IP rate limiter** (60/min, with `X-RateLimit-Remaining`),
  the `429` rail.
- **A `/api/health` endpoint** that reports whether the allowlists are locked.

The cache and limiter live per warm serverless instance — zero extra
infrastructure. A globally-shared version would need something like Vercel KV;
per-instance was the right trade for this traffic level.

## Layer 3 — the bypass I almost left behind

Here's the part worth the price of admission. I'd hardened `api/proxy.js`, shipped
it, verified the allowlist returned `403` for a bad host. Done, I thought.

It wasn't. The hardening went in as a fresh file, but the *original* repo still
contained sibling endpoints from the proxy's debugging days —
`api/debug-proxy.js`, `api/env-test.js`, an in-memory logging stack, a dashboard.
And **Vercel file-routes every `api/*.js` automatically.** `debug-proxy.js` was an
older, unguarded copy of the proxy — `ACAO: *`, no allowlist, no SSRF check — and
it was *live in production*, sitting right next to the locked-down one.

I caught it by probing the deployed endpoints rather than trusting the diff:

```text
GET /api/debug-proxy?url=https://example.com  ->  200, ACAO:*   (open relay!)
GET /api/proxy?url=https://example.com        ->  403           (correctly blocked)
```

The hardened front door was bolted; the side door was wide open. The fix was to
delete the entire dead surface — the debug and test endpoints, the logging stack,
the dashboard — and strip the few logging calls `proxy.js` still made into it.
That's the crossed-out path along the bottom of the diagram. Re-probing afterward,
both `debug-proxy` and `env-test` returned `404`, while the real proxy kept
returning `403` for bad hosts and `200` for allowed ones.

**The lesson:** when you harden something by writing a *new* clean version rather
than editing the vulnerable file in place, go hunting for the old siblings. A
framework that turns every file in a directory into a public route will happily
keep serving the one you forgot.

## Verifying against a real consumer

The satisfying part came from the production logs. Within minutes of the lockdown,
that background scanner's `?url=<random host>` probes were all returning `403` —
the open-relay abuse, shut. And when I loaded one of the apps that actually depends
on the proxy ([the grants visualizer](https://grants.noprofits.org)), its requests
sailed through: `200`s and `304`s against `projects.propublica.org`, each carrying
`Access-Control-Allow-Origin: https://grants.noprofits.org` — the scoped header, not
`*`. The allowed path works; everything else is turned away at a gate.

The proxy is still [open source](https://github.com/noprofits-org/cors-proxy-server),
still a single small function, still free to fork. It's just no longer an open door
with my name on it.

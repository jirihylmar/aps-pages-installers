---
name: public-addresses
description: How a page or endpoint a project serves for the operator gets a public development address - https://<label>.hub440-remote.cz/, opened only by the operator behind Cloudflare Access, asked for from the administrator side through the request mailbox, never built by the project. Use before exposing or sharing a page or endpoint beyond 127.0.0.1, when asked whether a page is reachable from outside, before any tunnel, DNS name, public port or Cloudflare credential, or when a page checks Host or Origin behind a public address.
---

# Public addresses

Read `.claude/skills/public-addresses/SKILL.md` completely and follow it: its rule section is the
agreed rule, word for word, and its numbered steps are the procedure.

In short: a page or endpoint served for the operator can get `https://<label>.hub440-remote.cz/`,
which only the operator opens, behind Cloudflare Access; the label names the service, never a host, a
person or an abbreviation. Ask the administrator side through the request mailbox, titled
`address: <label>`, with the host, the loopback port, what serves there and whether the page checks
Host or Origin. A page that checks Origin accepts the public one only with a `Cf-Access-Jwt-Assertion`
header. Record the answer in the `Public address` column of the README's `## Addresses` table. Never
create a tunnel, DNS name, public port or Cloudflare credential, never run `cloudflared`, and keep the
page on 127.0.0.1. Do not restate or reword the rule in Codex prose; the canonical file is the only
text.

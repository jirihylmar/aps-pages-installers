---
name: public-addresses
description: How a page or endpoint a project serves for the operator gets a public development address - https://<label>.hub440-remote.cz/, opened only by the operator behind Cloudflare Access, asked for from the administrator side through the request mailbox and never built by the project (no tunnel, DNS name, public port, Cloudflare credential or cloudflared of its own). Invoke before exposing, publishing or sharing a page or endpoint beyond 127.0.0.1, when asked whether a page is reachable from outside or how the operator opens it from anywhere, before creating any tunnel, DNS name, public port or Cloudflare credential, and when a page checks Host or Origin behind a public address.
---

# public-addresses

A page a project serves for the operator listens on 127.0.0.1 on its host. Most pages are opened from
the operator's workstation through a forward, and need nothing more. When the operator needs a page
from anywhere, it can also get a public development address. A project does not build that address:
the administrator side makes the DNS name, the tunnel route and the access rule in front of it. The
project asks for it, makes its page accept it, and records it.

This skill is information, not an order: it binds a project when it wants a page or endpoint reachable
beyond 127.0.0.1, and when it is asked whether one is.

A tunnel here is anything that makes a page reachable from outside its host: `cloudflared`, ngrok,
`ssh -R` and the like. A VPN route or a forward that an access rule already grants this project is not
what this rule is about, and stays as that rule says.

## The rule

Agreed on 2026-11-11. In the administrator side's session the operator said: *"yes, send it to the
engine, they distribute it, it has to be clear when the issue comes to question, everybody knows what
to do"*. In the engine's session the operator chose *"Roll out, with a skill (Recommended)"*.

<!-- RULE BEGIN -->
## Public addresses come from the administrator side

- **What can have one.** A page or endpoint a project serves for the operator (a preview, a test app, a dashboard, a sign-in page) can have a public development address.
- **Name.** `https://<label>.hub440-remote.cz/`. Its production twin would be `<label>.databridge.city`, for information only: nothing is served there from the estate. The label names the service (`sparks-models`, `sparks-monitor`, `chat`, `mcp`), never a host, a person or an abbreviation, and it is the same in both domains.
- **Who may open it.** Only the operator, behind Cloudflare Access (a one-time code sent to the operator's email addresses). Opening it to anyone else is asked first, the same way as the address itself.
- **How to get one.** Send a request to the administrator side through the request mailbox, titled `address: <label>`, with the host, the loopback port, what serves there, and whether the page checks Host or Origin. The administrator side creates the Access app, the tunnel route and the DNS name, and answers with the address.
- **What the page must accept.** The tunnel presents `Host: 127.0.0.1:<port>`, the same Host a local forward presents. The browser's Origin is `https://<label>.hub440-remote.cz`, so a page that checks Origin accepts that one too, and only together with a `Cf-Access-Jwt-Assertion` header, which Cloudflare Access adds to each request it lets through.
- **What the project keeps.** The public address, in the `Public address` column of its README's `## Addresses` table, beside the host, the port and what serves there. The cell stays empty until the administrator side has given an address.
- **What a project never does.** It never creates its own tunnel, DNS name, public port or Cloudflare credential, and never runs `cloudflared`. The page keeps listening on 127.0.0.1 only. The tunnel on each host is the administrator side's user unit `hyl-resources-manager-cloudflared`; a project neither stops nor edits it.
- **Changing it.** A new label, another port, a wider audience or the address's removal is asked for again, the same way. Nothing about the address is changed from the project's side.
- **When in doubt.** Whether a page is reachable from outside, and how, is answered by the README table and, where it says nothing, by a request; never by building something.
<!-- RULE END -->

## The steps

1. **Decide whether a public address is needed at all.** Most pages need none: the operator opens them
   at the address the README's `## Addresses` table already gives, through the project's forward. Ask
   for a public address only when the operator needs the page from somewhere that forward does not
   reach, and say so in the request. If nobody needs that, stop here.
2. **Pick the label.** It names the service, not where it runs or who uses it: `sparks-models`, never
   `vsb-157`, a person's name or `spm`. Lowercase letters, digits and hyphens. The same label would
   name the production twin at `<label>.databridge.city`, so choose the name the service would keep.
3. **Send the request** with `/syndicate-request`, to the administrator side: the receiver that skill
   names for accounts, hosts and access rules. Write the text to a file first:

   ```bash
   bash .claude/skills/syndicate-request/request.sh send \
     --to <the receiver for accounts, hosts and access rules> --title "address: <label>" < request.md
   ```

   In `request.md`: the host, the loopback port, what serves there, whether the page checks Host or
   Origin, and why the operator needs it from outside. No credential and nothing private: everyone
   with access to the mailbox reads it. Record the branch and commit `send` printed in
   `session_notes.md` and on the task that waits, and read the answer with `request.sh outcome
   '<branch>'` at each session start until it is closed. Do not wait in the session.
4. **Make the page accept the address.** A page that checks Host keeps accepting `127.0.0.1:<port>`,
   which is what the tunnel presents. A page that checks Origin also accepts
   `https://<label>.hub440-remote.cz`, and only on a request that carries a `Cf-Access-Jwt-Assertion`
   header; without that header the public Origin is refused. The page still binds 127.0.0.1 only.
5. **Record the answer** in README.md, in the `Public address` column of that page's row of the
   `## Addresses` table, in the commit that takes up the answer.
6. **Check it, bounded,** from any machine:

   ```bash
   curl -sI --max-time 15 https://<label>.hub440-remote.cz/ | sed -n '1p;/^location:/Ip'
   ```

   The address must answer `302` with a `location:` on the Cloudflare Access login
   (`https://<team>.cloudflareaccess.com/cdn-cgi/access/login/...`), and nothing else. A `200`, another
   status, or a redirect anywhere else means the page is not behind the operator's login: say so
   through the mailbox at once, under the same title.
7. **To change, widen or remove it, ask again** the same way, titled `address: <label>`, saying what
   changes. When the page is retired, ask for the address's removal, and empty its cell once the answer
   says it is gone.

## Why it exists

The pages the projects serve on the operator's hosts listen on 127.0.0.1, and many sit behind VPNs, so
the operator could open them only from the workstation, through a forward. To reach them from anywhere,
the administrator side runs one tunnel per host, with Cloudflare Access in front of every address, and
asked for this rule to reach every project: *"it has to be clear when the issue comes to question,
everybody knows what to do"*. A tunnel or public port a project made itself would be an address nobody
else knows about, with no login in front of it. One made centrally has one login, one place to read it
and one place to close it. The first is `https://sparks-models.hub440-remote.cz/`.

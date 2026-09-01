# ChainSafe ProPGF Attestations

Monthly operator-signed attestations for the Filecoin ProPGF grant covering
ChainSafe-operated Filecoin network infrastructure services:

- Mainnet and Calibnet bootstrap nodes
- Snapshot service (`forest-archive.chainsafe.dev`)
- Calibnet faucet (`faucet.calibnet.chainsafe-fil.io` and
  `forest-explorer.chainsafe.dev/faucet/calibnet`)
- Calibnet storage miner `t0181521`

Each monthly file lists the multiaddrs, wallet addresses, miner IDs, and
public artifacts that demonstrate ChainSafe operation of those services for
the month. Each file is introduced by a signed git commit. GitHub records
the signing key as "Verified" against a key registered to a ChainSafe
maintainer.

## Verifying an attestation

```sh
# Verify the introducing commit's signature locally
git log --show-signature -- propgf-attestations/<YYYY-MM>.md
```

Or, on GitHub, look for the "Verified" badge next to the commit on the file
history.

## Producing a new monthly attestation

Everything that changes month to month is collected by
[`collect.py`](collect.py):

```sh
./propgf-attestations/collect.py 2026-08
```

Then copy the previous month's file to `<YYYY-MM>.md` and update only:

1. Month names in the title, intro, section headings, and §5.
2. §1 — re-check the multiaddrs against the resolved TXT records and against
   the upstream Lotus bootstrap lists; only rewrite this section if they
   changed. Note any change (and link the upstream PR) the way the July 2026
   file documented the `/dnsaddr` migration.
3. §2 — the four `search=<YYYY-MM>` listing URLs, plus the file counts and
   first/last upload timestamps from `snapshots`.
4. §3 — `outgoing_transfers`, `lifetime_transfers`, `lifetime_messages`.
   Lifetime totals are trimmed to 23:59:59 UTC on the last day of the month.
5. §4 — `blocks_won` (round it; the exact count drifts as Filfox indexes),
   plus QAP, sector, and fault figures if they moved.
6. §6 — the `git log` path.

Counts are quoted as approximate on purpose: the Filfox list endpoints are
newest-first and grow while you page them, so two runs can differ by a few.

Commit with a signed commit (`git commit -S`) on a branch and open a PR — the
signature on the introducing commit is what the attestation relies on.

## ChainSafe-operated DNS

All bootstrap multiaddrs listed in these attestations use the
`chainsafe-fil.io` domain. Operator identity for the domain is verifiable
via public WHOIS and via the [`chainsafe.io`](https://chainsafe.io) website
linking to the same subdomains.

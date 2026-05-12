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

## ChainSafe-operated DNS

All bootstrap multiaddrs listed in these attestations use the
`chainsafe-fil.io` domain. Operator identity for the domain is verifiable
via public WHOIS and via the [`chainsafe.io`](https://chainsafe.io) website
linking to the same subdomains.

#!/usr/bin/env python3
"""Collect the per-month numbers needed for a ProPGF attestation file.

Usage:
    ./propgf-attestations/collect.py 2026-08

Prints a JSON blob with every value that changes month to month. Everything
else in the attestation (multiaddrs, wallet, miner ID, signing key) is static
and copied from the previous month's file.

Filfox list endpoints return newest-first, so the miner block count uses a
binary search over the page index instead of walking ~2500 pages.
"""

import concurrent.futures as cf
import datetime as dt
import functools
import json
import socket
import sys
import urllib.request

FAUCET = "t1lo4ajjyeygqn3lkrw6izwz6aft5chshngs6gjxa"
MINER = "t0181521"
FILFOX = "https://calibration.filfox.info/api/v1"
ARCHIVE = "https://forest-archive.chainsafe.dev"
BOOTSTRAP = [
    f"bootstrap-{net}-{i}.chainsafe-fil.io" for net in ("mainnet", "calibnet") for i in range(3)
]


def get(url):
    # forest-archive.chainsafe.dev 403s the default urllib User-Agent.
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def month_bounds(month):
    y, m = (int(x) for x in month.split("-"))
    start = dt.datetime(y, m, 1, tzinfo=dt.timezone.utc)
    end = dt.datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=dt.timezone.utc)
    return int(start.timestamp()), int(end.timestamp())


def iso(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def tcp_ok(host, port=34000):
    try:
        socket.create_connection((host, port), timeout=8).close()
        return True
    except OSError:
        return False


def snapshots(month):
    out = {}
    for net in ("mainnet", "calibnet"):
        for kind in ("diff", "lite"):
            d = get(f"{ARCHIVE}/list/{net}/{kind}?format=json&search={month}")
            items = d["items"]
            out[f"{net}/{kind}"] = {
                "count": d["total"],
                "first_uploaded": items[-1]["uploaded"] if items else None,
                "last_uploaded": items[0]["uploaded"] if items else None,
            }
    return out


def faucet(start, end):
    """Walk transfers newest-first until before `start`. A month is a few
    hundred rows, so this is cheap. Also returns lifetime counts trimmed to
    the end of the month."""
    outgoing = after = page = 0
    total = None
    done = False
    while not done:
        d = get(f"{FILFOX}/address/{FAUCET}/transfers?pageSize=100&page={page}")
        total = total if total is not None else d["totalCount"]
        items = d.get("transfers", [])
        if not items:
            break
        for t in items:
            if t["timestamp"] >= end:
                after += 1
                continue
            if t["timestamp"] < start:
                done = True
                break
            if t.get("type") == "send" and t.get("from") == FAUCET:
                outgoing += 1
        page += 1

    msgs_after, page = 0, 0
    msgs_total = None
    while True:
        d = get(f"{FILFOX}/address/{FAUCET}/messages?pageSize=100&page={page}")
        msgs_total = msgs_total if msgs_total is not None else d["totalCount"]
        items = d.get("messages", [])
        if not items or items[-1]["timestamp"] < end:
            msgs_after += sum(1 for m in items if m["timestamp"] >= end)
            break
        msgs_after += len(items)
        page += 1

    return {
        "outgoing_transfers": outgoing,
        "lifetime_transfers": total - after,
        "lifetime_messages": msgs_total - msgs_after,
    }


def miner_blocks(start, end):
    @functools.lru_cache(maxsize=None)
    def page(p):
        d = get(f"{FILFOX}/address/{MINER}/blocks?pageSize=100&page={p}")
        return d["totalCount"], tuple(b["timestamp"] for b in d["blocks"])

    total, _ = page(0)

    def ts(i):
        return page(i // 100)[1][i % 100]

    def first_below(x):  # list is descending by timestamp
        lo, hi = 0, total
        while lo < hi:
            mid = (lo + hi) // 2
            if ts(mid) < x:
                hi = mid
            else:
                lo = mid + 1
        return lo

    hi_i, lo_i = first_below(end), first_below(start)
    return {
        "blocks_won": lo_i - hi_i,
        "first_block": iso(ts(lo_i - 1)),
        "last_block": iso(ts(hi_i)),
        "lifetime_blocks": total,
    }


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    month = sys.argv[1]
    start, end = month_bounds(month)

    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        f_snap = ex.submit(snapshots, month)
        f_faucet = ex.submit(faucet, start, end)
        f_blocks = ex.submit(miner_blocks, start, end)
        f_tcp = ex.submit(lambda: {h: tcp_ok(h) for h in BOOTSTRAP})
        info = get(f"{FILFOX}/address/{MINER}")["miner"]

        result = {
            "month": month,
            "bootstrap_tcp_34000": f_tcp.result(),
            "snapshots": f_snap.result(),
            "faucet": f_faucet.result(),
            "miner": {
                **f_blocks.result(),
                "qap_tib": round(int(info["qualityAdjPower"]) / 2**40, 2),
                "active_sectors": info["sectors"]["active"],
                "faults": info["sectors"]["faulty"],
                "peer_id": info["peerId"],
                "owner": info["owner"]["address"],
            },
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

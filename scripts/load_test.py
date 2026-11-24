#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import time

def request(url):
    start = time.perf_counter()
    try:
        with urlopen(url, timeout=5) as r:
            r.read()
            return r.status, time.perf_counter() - start
    except HTTPError as e:
        return e.code, time.perf_counter() - start
    except URLError:
        return 0, time.perf_counter() - start

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://localhost:8080/api/orders")
    p.add_argument("--requests", type=int, default=300)
    p.add_argument("--concurrency", type=int, default=15)
    a = p.parse_args()
    start = time.perf_counter()
    out = []
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futures = [ex.submit(request, a.url) for _ in range(a.requests)]
        for f in as_completed(futures):
            out.append(f.result())
    elapsed = time.perf_counter() - start
    ok = sum(200 <= status < 400 for status, _ in out)
    print(f"total={len(out)} success={ok} failed={len(out)-ok} elapsed={elapsed:.2f}s")
    print(f"throughput={len(out)/elapsed:.2f} req/s")

if __name__ == "__main__":
    main()

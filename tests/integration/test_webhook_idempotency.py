import threading
import time
import requests

BASE = "http://127.0.0.1:5000/webhook"


def post_event(event_id, payload):
    r = requests.post(BASE, headers={"X-Event-ID": event_id, "Content-Type": "application/json"}, json={"message": payload})
    return r.status_code, r.json()


def test_idempotency_duplicate():
    event_id = "test-evt-dup-1"
    s1 = post_event(event_id, "BUY BTCUSD price:45000")
    s2 = post_event(event_id, "BUY BTCUSD price:45000")
    assert s1[0] == 200
    # second response should be duplicate:true
    assert s2[0] == 200
    assert s2[1].get("duplicate") is True


def test_concurrent_duplicates():
    event_id = "test-evt-concurrent-1"
    results = []

    def worker():
        results.append(post_event(event_id, "BUY BTCUSD price:45000"))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # At least one should be duplicate or only one processed
    duplicates = sum(1 for code, body in results if body.get("duplicate"))
    assert duplicates >= 1

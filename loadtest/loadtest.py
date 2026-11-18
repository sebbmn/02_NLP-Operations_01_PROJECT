"""Simple load generator: sends random test comments to the classifier.

Usage: python3 loadtest/loadtest.py [--users 10] [--duration 120] [--url ...]
Uses only the Python standard library, no installation needed.
"""

import argparse
import json
import random
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

COMMENTS = [
    "Die Zahlen im Artikel stimmen nicht, das Bundesamt nennt andere Werte.",
    "Mir fehlt die Sicht der Gegenseite, der Artikel ist sehr einseitig.",
    "Gute Zusammenfassung, kurz und verständlich. Danke!",
    "Endlich spricht das mal jemand an, ich bin völlig einverstanden.",
    "Weiss jemand, ab wann die neue Regel gilt?",
    "Gibt es dazu eine Quelle oder eine Studie?",
    "Wow, schon wieder eine Preiserhöhung. Was für eine Überraschung.",
    "Klar, und nächste Woche fliegen die Schweine.",
    "Das ist eine absolute Frechheit, die da oben machen sowieso, was sie wollen!",
    "Unfassbar, wer so etwas entscheidet, gehört sofort abgesetzt!",
    "Hat jemand das Spiel gestern Abend gesehen?",
    "Jetzt günstig Krypto kaufen, Link in meinem Profil!",
    "Ich habe den Artikel nicht gelesen, aber ich bin trotzdem dagegen.",
    "Die Argumente sind nachvollziehbar, aber die Kosten werden unterschätzt.",
    "Toller Beitrag, bitte mehr davon.",
    "Was bedeutet das konkret für Mieter in Zürich?",
]


def send_comment(url: str) -> bool:
    body = json.dumps({"comment": random.choice(COMMENTS)}).encode()
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status == 200
    except Exception:
        return False


def user(url: str, end_time: float) -> tuple[int, int]:
    """One simulated user: sends comments one after another until the time is up."""
    ok, failed = 0, 0
    while time.monotonic() < end_time:
        if send_comment(url):
            ok += 1
        else:
            failed += 1
        time.sleep(random.uniform(0, 0.5))
    return ok, failed


def main():
    parser = argparse.ArgumentParser(description="Load test for the comment classifier")
    parser.add_argument("--url", default="http://localhost:8080/classify")
    parser.add_argument("--users", type=int, default=10, help="number of parallel users")
    parser.add_argument("--duration", type=int, default=120, help="duration in seconds")
    args = parser.parse_args()

    print(f"Sending comments with {args.users} users for {args.duration}s to {args.url}")
    end_time = time.monotonic() + args.duration

    with ThreadPoolExecutor(max_workers=args.users) as pool:
        results = list(pool.map(lambda _: user(args.url, end_time), range(args.users)))

    ok = sum(r[0] for r in results)
    failed = sum(r[1] for r in results)
    print(f"Done: {ok} successful, {failed} failed requests")


if __name__ == "__main__":
    main()

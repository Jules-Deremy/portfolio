"""
RLC Token Analysis — Data Fetcher
Fetches all query results from Dune Analytics API
and saves them as CSV files for further analysis.
"""

import requests
import json
import time
import csv
import os
from datetime import datetime

# ── Config ──────────────────────────────────────────────
DUNE_API_KEY = "KloPNhj1xmLzLv9E2h2X3TzUgjYGXvgq" 
OUTPUT_DIR = "data"

QUERIES = {
    "rlc_daily_activity":  6906318,
    "rlc_top_receivers":   6906356,
    "rlc_monthly_activity": 6906399,
    "rlc_dex_activity":    6921501,
    "rlc_august_peak":     6921513,
    "rlc_march_peak":      6921524,
}

HEADERS = {
    "X-DUNE-API-KEY": DUNE_API_KEY,
    "Content-Type": "application/json",
}

BASE_URL = "https://api.dune.com/api/v1"

# ── Fonctions ────────────────────────────────────────────

def execute_query(query_id):
    """Lance l'exécution d'une requête Dune."""
    url = f"{BASE_URL}/query/{query_id}/execute"
    response = requests.post(url, headers=HEADERS)
    data = response.json()
    if "execution_id" not in data:
        raise Exception(f"Erreur exécution query {query_id}: {data}")
    return data["execution_id"]


def get_execution_status(execution_id):
    """Vérifie le statut d'une exécution."""
    url = f"{BASE_URL}/execution/{execution_id}/status"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def get_execution_results(execution_id):
    """Récupère les résultats d'une exécution."""
    url = f"{BASE_URL}/execution/{execution_id}/results"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def wait_for_completion(execution_id, query_name, timeout=120):
    """Attend la fin d'une exécution avec polling."""
    print(f"  Exécution en cours", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        status_data = get_execution_status(execution_id)
        state = status_data.get("state", "")
        if state == "QUERY_STATE_COMPLETED":
            print(" done.")
            return True
        elif state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"):
            print(f" FAILED: {state}")
            return False
        print(".", end="", flush=True)
        time.sleep(3)
    print(" TIMEOUT")
    return False


def save_to_csv(rows, columns, filename):
    """Sauvegarde les résultats en CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return filepath


def fetch_query(name, query_id):
    """Exécute une requête et sauvegarde les résultats."""
    print(f"\n[{name}] — query {query_id}")
    try:
        execution_id = execute_query(query_id)
        success = wait_for_completion(execution_id, name)
        if not success:
            print(f"  Skipped.")
            return None

        results = get_execution_results(execution_id)
        rows = results.get("result", {}).get("rows", [])
        metadata = results.get("result", {}).get("metadata", {})
        columns = metadata.get("column_names", [])

        if not rows:
            print(f"  No data returned.")
            return None

        filepath = save_to_csv(rows, columns, f"{name}.csv")
        print(f"  Saved {len(rows)} rows → {filepath}")
        return filepath

    except Exception as e:
        print(f"  Error: {e}")
        return None


# ── Main ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("RLC Token Analysis — Dune Data Fetcher")
    print(f"Started at {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

    results = {}
    for name, query_id in QUERIES.items():
        filepath = fetch_query(name, query_id)
        results[name] = filepath

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    for name, path in results.items():
        status = f"✓ {path}" if path else "✗ Failed"
        print(f"  {name}: {status}")
    print(f"\nDone at {datetime.now().strftime('%H:%M:%S')}")
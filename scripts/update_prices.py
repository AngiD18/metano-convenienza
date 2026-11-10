#!/usr/bin/env python3
"""Importa prezzi metano MIMIT verificando l'identità dei distributori."""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.mimit.gov.it/images/exportCSV/"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "prices.json"
STATIONS = {
    "arz": {"id": "14486", "city": "piove di sacco", "words": ("borgo", "botteghe")},
    "can": {"id": "56676", "city": "candiana", "words": ("mare",)},
    "eni": {"id": "13223", "city": "padova", "words": ("stati", "uniti")},
}

def norm(value: str) -> str:
    s = unicodedata.normalize("NFKD", str(value or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z\d]+", " ", s.lower())).strip()

def download(filename: str) -> str:
    req = urllib.request.Request(
        BASE + filename,
        headers={"User-Agent": "MetanoConfronto/1.0", "Accept": "text/csv,*/*"},
    )
    with urllib.request.urlopen(req, timeout=50) as r:
        body = r.read(25000000)
    if len(body) < 1000:
        raise RuntimeError("File MIMIT vuoto o troncato: " + filename)
    return body.decode("utf-8-sig", errors="replace")

def records(content: str, field: str) -> list[dict[str, str]]:
    lines = content.replace("\r\n", "\n").splitlines()
    header = next(
        (i for i, line in enumerate(lines[:8])
         if "idimpianto" in line.lower() and field.lower() in line.lower()), -1)
    if header < 0:
        raise RuntimeError("Formato CSV ministeriale non riconosciuto: " + field)
    delim = "|" if lines[header].count("|") > lines[header].count(";") else ";"
    result = list(csv.DictReader(io.StringIO("\n".join(lines[header:])), delimiter=delim))
    return [{str(k).strip(): v for k, v in row.items()} for row in result]

def ident(row: dict) -> str:
    return str(row.get("idImpianto", row.get("idimpianto", ""))).strip()

def identify(rows: list[dict]) -> dict[str, str]:
    output = {}
    for key, station in STATIONS.items():
        candidates = []
        for row in rows:
            if norm(row.get("Comune")) != station["city"]:
                continue
            address_words = norm(row.get("Indirizzo")).split()
            if all(w in address_words for w in station["words"]):
                candidates.append(row)
        exact = [row for row in candidates if ident(row) == station["id"]]
        if len(exact) == 1:
            output[key] = ident(exact[0])
        elif len(candidates) == 1:
            output[key] = ident(candidates[0])
            print("Impianto", key, "identificato dall'indirizzo", output[key])
        else:
            print("Impianto non identificato in modo univoco:", key, file=sys.stderr)
    return output

def official_prices(rows: list[dict], ids: dict[str, str]) -> dict:
    by_id = {v: k for k, v in ids.items()}
    found = {}
    for row in rows:
        key = by_id.get(ident(row))
        if not key or norm(row.get("descCarburante")) != "metano":
            continue
        try:
            price = float(str(row.get("prezzo", "")).replace(",", "."))
        except ValueError:
            continue
        if not (0.5 < price < 6.0):
            continue
        is_self = str(row.get("isSelf", "")).strip()
        previous = found.get(key)
        if previous is None or (previous.get("_self") == "1" and is_self == "0"):
            found[key] = {
                "price": round(price, 3),
                "reported_at": str(row.get("dtComu", "")).strip(),
                "status": "official",
                "source": "MIMIT",
                "_self": is_self,
            }
    for row in found.values():
        row.pop("_self", None)
    return found

def main():
    registry = records(download("anagrafica_impianti_attivi.csv"), "Gestore")
    ids = identify(registry)
    if not ids:
        raise RuntimeError("Nessun distributore identificato: non modifico i prezzi")
    prices = records(download("prezzo_alle_8.csv"), "descCarburante")
    found = official_prices(prices, ids)
    if not found:
        raise RuntimeError("Nessun prezzo metano verificabile: non modifico i prezzi")
    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "MIMIT – Osservaprezzi Carburanti",
        "stations": {**existing.get("stations", {}), **found},
    }
    OUTPUT.parent.mkdir(exist_ok=True, parents=True)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Prezzi aggiornati:", ", ".join(found), "(altri valori conservati)")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Schadensmanagement-System – Interaktive CLI
Richtpreise Schadensabrechnung Neu 2026

Verwendung:
  python main.py
  python main.py --demo
  python main.py --kunde "Musterfirma GmbH" --objekt "Container A3" \
                 --schaden "2x Türklinke, 1 Heizkörper, 3 LED-Röhren"
"""

import argparse
import sys
import textwrap
from damage_agents import SchadensMasterAgent
from price_list import PRICE_LIST


DEMO_SCHADEN = (
    "2x Türklinke, 1 Heizkörper, 3 LED-Leuchtstoffröhre, "
    "1 Klobrille inkl. Montage, 2 Steckdose, Reinigungsstunde 2"
)


def preisliste_anzeigen() -> None:
    print("\n── VERFÜGBARE POSITIONEN (Auszug) ──────────────────────────────────")
    kategorien: dict[str, list] = {}
    for eintrag in PRICE_LIST:
        kategorien.setdefault(eintrag["kategorie"], []).append(eintrag)
    for kat, eintraege in sorted(kategorien.items()):
        print(f"\n  [{kat}]")
        for e in eintraege:
            hinweis = f"  ({e['hinweis']})" if e.get("hinweis") else ""
            print(f"    • {e['bezeichnung']:<45} {e['preis']:>8.2f} € / {e['einheit']}{hinweis}")


def interaktiver_modus(agent: SchadensMasterAgent) -> None:
    print(textwrap.dedent("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║       SCHADENSMANAGEMENT-SYSTEM  –  Richtpreise 2026            ║
    ║       Container- und Raumsysteme                                 ║
    ╚══════════════════════════════════════════════════════════════════╝

    Befehle:
      'liste'  – Verfügbare Positionen anzeigen
      'ende'   – Programm beenden

    Eingabeformat für Schäden:
      Menge × Bezeichnung, z. B.:
      "2x Türklinke, 1 Heizkörper, 3 LED-Röhren, Reinigungsstunde 2"
    """))

    while True:
        print("-" * 68)
        kunde = input("  Kundenname          : ").strip() or "Unbekannt"
        objekt = input("  Objektbezeichnung   : ").strip() or "k. A."

        schaden = input("\n  Schadensangaben     : ").strip()
        if schaden.lower() == "ende":
            break
        if schaden.lower() == "liste":
            preisliste_anzeigen()
            continue
        if not schaden:
            print("  Keine Angaben. Bitte Schäden eingeben.")
            continue

        zusatz_raw = input(
            "  Zusätzliche Montage (Std., 0 wenn keine): "
        ).strip().replace(",", ".")
        try:
            zusatz = float(zusatz_raw) if zusatz_raw else 0.0
        except ValueError:
            zusatz = 0.0

        print()
        result = agent.verarbeite(
            schaden,
            kunde=kunde,
            objekt=objekt,
            zusatz_montage_stunden=zusatz,
        )
        print(result)

        weiter = input("\n  Neue Schadensmeldung? [j/n]: ").strip().lower()
        if weiter != "j":
            break

    print("\n  Auf Wiedersehen.\n")


def cli_modus(args: argparse.Namespace, agent: SchadensMasterAgent) -> None:
    result = agent.verarbeite(
        args.schaden,
        kunde=args.kunde or "",
        objekt=args.objekt or "",
        zusatz_montage_stunden=args.montage or 0.0,
    )
    print(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Schadensmanagement-System – Richtpreise 2026"
    )
    parser.add_argument("--kunde", help="Kundenname")
    parser.add_argument("--objekt", help="Objektbezeichnung")
    parser.add_argument(
        "--schaden",
        help='Schadensangaben, z. B. "2x Türklinke, 1 Heizkörper"',
    )
    parser.add_argument(
        "--montage",
        type=float,
        default=0.0,
        help="Zusätzliche Montagestunden (über Pauschalen hinaus)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Demo-Schadensmeldung ausführen",
    )
    parser.add_argument(
        "--liste",
        action="store_true",
        help="Preisliste anzeigen und beenden",
    )
    args = parser.parse_args()

    agent = SchadensMasterAgent()

    if args.liste:
        preisliste_anzeigen()
        sys.exit(0)

    if args.demo:
        print("  [DEMO-MODUS]\n")
        result = agent.verarbeite(
            DEMO_SCHADEN,
            kunde="Musterfirma GmbH",
            objekt="Bürocontainer BK-07 / Baustelle Nord",
            zusatz_montage_stunden=1.5,
        )
        print(result)
        sys.exit(0)

    if args.schaden:
        cli_modus(args, agent)
        sys.exit(0)

    interaktiver_modus(agent)


if __name__ == "__main__":
    main()

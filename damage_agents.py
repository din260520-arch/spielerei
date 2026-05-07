"""
Schadensmanagement-System – Multi-Agent-Architektur
Richtpreise Schadensabrechnung Neu 2026
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date
from difflib import SequenceMatcher
from typing import Optional
from price_list import PRICE_LIST


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SchadensPosition:
    bezeichnung: str
    kategorie: str
    menge: float
    einheit: str
    einzelpreis: float
    gesamtpreis: float
    hinweis: str = ""
    montage_extra: float = 0.0


@dataclass
class SchadensReport:
    kunde: str
    objekt: str
    meldung_text: str
    positionen: list[SchadensPosition] = field(default_factory=list)
    zusatz_montage_stunden: float = 0.0
    erfassungsdatum: str = field(default_factory=lambda: date.today().strftime("%d.%m.%Y"))

    @property
    def zwischensumme(self) -> float:
        return sum(p.gesamtpreis for p in self.positionen)

    @property
    def montage_extra_gesamt(self) -> float:
        extra = sum(p.montage_extra * p.menge for p in self.positionen)
        extra += self.zusatz_montage_stunden * 68.0
        return extra

    @property
    def gesamtsumme(self) -> float:
        return self.zwischensumme + self.montage_extra_gesamt


# ---------------------------------------------------------------------------
# Sub-Agent 1: Analyst-Agent
# ---------------------------------------------------------------------------

class AnalystAgent:
    """
    Parses free-text damage descriptions into structured position requests.

    Input format examples:
      - "2x Türklinke, 1 Heizkörper, 3 LED-Röhren"
      - "Türklinken (2 Stück), Steckdose 1x, Reinigung Nikotin"
    """

    _MENGE_PATTERN = re.compile(
        r"""
        (?:
            (\d+(?:[.,]\d+)?)\s*[xX×]\s*(.+?)   # e.g. 2x Türklinke
            |
            (.+?)\s+(\d+(?:[.,]\d+)?)\s*(?:Stück|stk|st|x)?  # e.g. Türklinke 2
            |
            (.+?)\s*\((\d+(?:[.,]\d+)?)\s*(?:Stück|stk|st)?\)  # e.g. Türklinke (2)
        )
        """,
        re.VERBOSE | re.IGNORECASE,
    )

    def analyse(self, raw_input: str, kunde: str = "", objekt: str = "") -> dict:
        """Return structured damage context from raw user text."""
        positionen_roh = self._split_positions(raw_input)
        parsed = []
        for pos in positionen_roh:
            menge, bezeichnung = self._extract_menge(pos)
            if bezeichnung:
                parsed.append({"bezeichnung": bezeichnung.strip(), "menge": menge})

        return {
            "kunde": kunde or "Unbekannt",
            "objekt": objekt or "k. A.",
            "raw_input": raw_input,
            "positionen_roh": parsed,
        }

    @staticmethod
    def _split_positions(text: str) -> list[str]:
        """Split by commas, semicolons, or newlines."""
        parts = re.split(r"[,;\n]+", text)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def _extract_menge(text: str) -> tuple[float, str]:
        """Extract quantity and item name from a single position string."""
        # Pattern: number then text  (e.g. "2 Türklinken", "2x Türklinken")
        m = re.match(r"^(\d+(?:[.,]\d+)?)\s*[xX×]?\s+(.+)$", text)
        if m:
            menge = float(m.group(1).replace(",", "."))
            return menge, m.group(2)

        # Pattern: text then number  (e.g. "Türklinken 2", "Türklinken (2 Stück)")
        m = re.match(r"^(.+?)\s+(\d+(?:[.,]\d+)?)\s*(?:Stück|stk|st\.?)?$", text, re.IGNORECASE)
        if m:
            menge = float(m.group(2).replace(",", "."))
            return menge, m.group(1)

        m = re.match(r"^(.+?)\s*\((\d+(?:[.,]\d+)?)\s*(?:Stück|stk|st\.?)?\)$", text, re.IGNORECASE)
        if m:
            menge = float(m.group(2).replace(",", "."))
            return menge, m.group(1)

        return 1.0, text


# ---------------------------------------------------------------------------
# Sub-Agent 2: Kalkulator-Agent
# ---------------------------------------------------------------------------

class KalkulatorAgent:
    """
    Matches analysed positions against the price list and calculates totals.
    Uses fuzzy matching to find the closest entry when no exact match is found.
    """

    def __init__(self, price_list: list[dict]):
        self.price_list = price_list

    def berechne(
        self,
        analyse_result: dict,
        zusatz_montage_stunden: float = 0.0,
    ) -> SchadensReport:
        report = SchadensReport(
            kunde=analyse_result["kunde"],
            objekt=analyse_result["objekt"],
            meldung_text=analyse_result["raw_input"],
            zusatz_montage_stunden=zusatz_montage_stunden,
        )

        for pos_roh in analyse_result["positionen_roh"]:
            eintrag = self._finde_preis(pos_roh["bezeichnung"])
            if eintrag is None:
                continue

            menge = pos_roh["menge"]
            einzelpreis = eintrag["preis"]
            montage_extra = eintrag.get("montage", 0.0)

            report.positionen.append(
                SchadensPosition(
                    bezeichnung=eintrag["bezeichnung"],
                    kategorie=eintrag["kategorie"],
                    menge=menge,
                    einheit=eintrag["einheit"],
                    einzelpreis=einzelpreis,
                    gesamtpreis=round(einzelpreis * menge, 2),
                    hinweis=eintrag.get("hinweis", ""),
                    montage_extra=montage_extra,
                )
            )

        return report

    def _finde_preis(self, suchbegriff: str) -> Optional[dict]:
        """Find best matching price list entry for a search term."""
        suchbegriff_norm = suchbegriff.lower().strip()

        # 1. Exact match (case-insensitive)
        for eintrag in self.price_list:
            if eintrag["bezeichnung"].lower().strip() == suchbegriff_norm:
                return eintrag

        # 2. Substring match
        treffer = [
            e for e in self.price_list
            if suchbegriff_norm in e["bezeichnung"].lower()
            or e["bezeichnung"].lower() in suchbegriff_norm
        ]
        if len(treffer) == 1:
            return treffer[0]
        if len(treffer) > 1:
            # Prefer shortest (most specific) match
            return min(treffer, key=lambda e: len(e["bezeichnung"]))

        # 3. Token overlap match
        tokens_suche = set(re.split(r"\W+", suchbegriff_norm))
        bester_score = 0.0
        bester_eintrag = None
        for eintrag in self.price_list:
            tokens_eintrag = set(re.split(r"\W+", eintrag["bezeichnung"].lower()))
            gemeinsam = tokens_suche & tokens_eintrag
            if not gemeinsam:
                continue
            score = len(gemeinsam) / max(len(tokens_suche), len(tokens_eintrag))
            if score > bester_score:
                bester_score = score
                bester_eintrag = eintrag

        if bester_score >= 0.3:
            return bester_eintrag

        # 4. Fuzzy sequence match
        bester_fuzzy = max(
            self.price_list,
            key=lambda e: SequenceMatcher(
                None, suchbegriff_norm, e["bezeichnung"].lower()
            ).ratio(),
        )
        ratio = SequenceMatcher(
            None, suchbegriff_norm, bester_fuzzy["bezeichnung"].lower()
        ).ratio()
        if ratio >= 0.5:
            return bester_fuzzy

        return None


# ---------------------------------------------------------------------------
# Sub-Agent 3: Qualitäts-Agent
# ---------------------------------------------------------------------------

class QualitaetsAgent:
    """
    Validates that matched categories are plausible for the search terms.
    Flags suspicious matches for human review.
    """

    _WARNUNG_SCHWELLE = 0.6  # similarity threshold below which a warning is issued

    def pruefen(self, report: SchadensReport, analyse_result: dict) -> list[str]:
        warnungen = []
        roh_liste = [p["bezeichnung"].lower() for p in analyse_result["positionen_roh"]]

        for pos in report.positionen:
            # Find best similarity against any of the raw search terms
            bester = max(
                (SequenceMatcher(None, roh, pos.bezeichnung.lower()).ratio()
                 for roh in roh_liste),
                default=0.0,
            )
            if bester < self._WARNUNG_SCHWELLE:
                bester_roh = max(
                    roh_liste,
                    key=lambda r: SequenceMatcher(None, r, pos.bezeichnung.lower()).ratio(),
                )
                warnungen.append(
                    f"Mögliche Fehlanpassung: Gesucht '{bester_roh}' → "
                    f"Gefunden '{pos.bezeichnung}' (Kategorie: {pos.kategorie}). "
                    f"Bitte prüfen."
                )

        # Check that found positions have valid prices
        for pos in report.positionen:
            if pos.einzelpreis <= 0:
                warnungen.append(
                    f"Kein Richtpreis hinterlegt für '{pos.bezeichnung}'. "
                    f"Manuelle Preisermittlung erforderlich."
                )

        return warnungen


# ---------------------------------------------------------------------------
# Sub-Agent 4: Kommunikations-Agent
# ---------------------------------------------------------------------------

class KommunikationsAgent:
    """
    Generates the final formatted output: summary, cost table, and customer letter.
    """

    def erstelle_output(
        self,
        report: SchadensReport,
        warnungen: list[str],
    ) -> str:
        sections: list[str] = []

        sections.append(self._header(report))
        sections.append(self._zusammenfassung(report))
        sections.append(self._kostentabelle(report))
        if warnungen:
            sections.append(self._warnungen(warnungen))
        sections.append(self._anschreiben(report))

        return "\n\n".join(sections)

    # ---- private helpers ---------------------------------------------------

    @staticmethod
    def _header(report: SchadensReport) -> str:
        sep = "=" * 72
        return "\n".join([
            sep,
            "  SCHADENSABRECHNUNG  –  Richtpreise 2026",
            sep,
            f"  Datum  : {report.erfassungsdatum}",
            f"  Kunde  : {report.kunde}",
            f"  Objekt : {report.objekt}",
        ])

    @staticmethod
    def _zusammenfassung(report: SchadensReport) -> str:
        lines = ["── ZUSAMMENFASSUNG DER ERFASSTEN SCHÄDEN ──────────────────────"]
        for i, pos in enumerate(report.positionen, 1):
            lines.append(f"  {i:2}. {pos.bezeichnung}  ×  {pos.menge:.0f}  [{pos.kategorie}]")
        return "\n".join(lines)

    @staticmethod
    def _kostentabelle(report: SchadensReport) -> str:
        header = (
            "── DETAILLIERTE KOSTENAUFSTELLUNG ─────────────────────────────\n"
            f"  {'Pos':<4} {'Bezeichnung':<38} {'Menge':>6} "
            f"{'Einzelpreis':>12} {'Gesamtpreis':>12}\n"
            "  " + "-" * 68
        )
        rows = [header]
        for i, pos in enumerate(report.positionen, 1):
            zeile = (
                f"  {i:<4} {pos.bezeichnung:<38} {pos.menge:>6.0f} "
                f"{pos.einzelpreis:>11.2f}€ {pos.gesamtpreis:>11.2f}€"
            )
            if pos.hinweis:
                zeile += f"\n       Hinweis: {pos.hinweis}"
            if pos.montage_extra > 0:
                montage_gesamt = pos.montage_extra * pos.menge
                zeile += (
                    f"\n       + Montagepauschale: {pos.montage_extra:.2f}€ × "
                    f"{pos.menge:.0f} = {montage_gesamt:.2f}€"
                )
            rows.append(zeile)

        rows.append("  " + "-" * 68)

        if report.montage_extra_gesamt > 0 and report.zusatz_montage_stunden > 0:
            rows.append(
                f"  {'Zus. Montage':<43} "
                f"{report.zusatz_montage_stunden:>6.1f}h "
                f"{'68,00€/h':>12} "
                f"{report.zusatz_montage_stunden * 68:>11.2f}€"
            )

        rows.append(
            f"\n  {'ZWISCHENSUMME (Teile):':<50} {report.zwischensumme:>11.2f}€"
        )
        if report.montage_extra_gesamt > 0:
            rows.append(
                f"  {'MONTAGEPAUSCHALEN:':<50} {report.montage_extra_gesamt:>11.2f}€"
            )
        rows.append(
            f"  {'GESAMTSUMME (netto):':<50} {report.gesamtsumme:>11.2f}€"
        )

        return "\n".join(rows)

    @staticmethod
    def _warnungen(warnungen: list[str]) -> str:
        lines = ["── HINWEISE / PRÜFBEDARF ───────────────────────────────────────"]
        for w in warnungen:
            lines.append(f"  ⚠  {w}")
        return "\n".join(lines)

    @staticmethod
    def _anschreiben(report: SchadensReport) -> str:
        positionen_text = "\n".join(
            f"   – {pos.bezeichnung} ({pos.menge:.0f} Stück/Einheit): "
            f"{pos.gesamtpreis:.2f} €"
            for pos in report.positionen
        )

        return (
            "── ENTWURF KUNDENANSCHREIBEN ────────────────────────────────────\n\n"
            f"Betreff: Schadensmeldung – Objekt {report.objekt}\n\n"
            f"Sehr geehrte Damen und Herren,\n\n"
            f"im Rahmen der Abnahme bzw. Rückgabe des oben genannten Objekts wurden "
            f"folgende Beschädigungen festgestellt, die über den vertraglich "
            f"vereinbarten Normalverschleiß hinausgehen. Wir bitten Sie, die "
            f"entstandenen Kosten zu tragen.\n\n"
            f"Schadensübersicht:\n"
            f"{positionen_text}\n\n"
            f"Gesamtbetrag (netto): {report.gesamtsumme:.2f} €\n\n"
            f"Bitte überweisen Sie den ausstehenden Betrag innerhalb von 14 Tagen "
            f"auf unser Ihnen bekanntes Konto. Bei Rückfragen stehen wir Ihnen "
            f"selbstverständlich gerne zur Verfügung.\n\n"
            f"Mit freundlichen Grüßen\n\n"
            f"[Unterschrift / Firmenstempel]"
        )


# ---------------------------------------------------------------------------
# Master-Agent
# ---------------------------------------------------------------------------

class SchadensMasterAgent:
    """
    Orchestrates Analyst → Kalkulator → Qualität → Kommunikation.
    """

    def __init__(self):
        self.analyst = AnalystAgent()
        self.kalkulator = KalkulatorAgent(PRICE_LIST)
        self.qualitaet = QualitaetsAgent()
        self.kommunikation = KommunikationsAgent()

    def verarbeite(
        self,
        schadenstext: str,
        kunde: str = "",
        objekt: str = "",
        zusatz_montage_stunden: float = 0.0,
    ) -> str:
        # Step 1: Analyst
        analyse = self.analyst.analyse(schadenstext, kunde=kunde, objekt=objekt)

        # Step 2: Kalkulator
        report = self.kalkulator.berechne(analyse, zusatz_montage_stunden)

        # Step 3: Qualität
        warnungen = self.qualitaet.pruefen(report, analyse)

        # Step 4: Kommunikation
        return self.kommunikation.erstelle_output(report, warnungen)

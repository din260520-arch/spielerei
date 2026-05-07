"""
Richtpreise Schadensabrechnung Neu 2026
Price list for container and room systems damage settlement.
"""

PRICE_LIST = [
    # Heizung
    {"kategorie": "Heizung", "typ": "Ersatzteil", "bezeichnung": "Heizkörper", "preis": 179.0, "einheit": "je Stück", "hinweis": ""},

    # Tür
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Türschließer", "preis": 129.0, "einheit": "je Stück", "hinweis": "zzgl. Montage 109€", "montage": 109.0},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Zylinder inkl. Montage", "preis": 34.9, "einheit": "je Stück", "hinweis": "Schlüssel fehlen: 27,90€"},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Spezialschloss für WC05/08 inkl. Montage", "preis": 95.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Türklinke", "preis": 21.4, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Türschließblech", "preis": 19.8, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Türblatt komplett", "preis": 279.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Türpaneel", "preis": 595.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Türbeschlag komplett inkl. Klinke", "preis": 39.85, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Tür Zarge", "preis": 279.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Schlossaufbruch", "preis": 29.5, "einheit": "je Stück", "hinweis": "= 30 min Montage"},
    {"kategorie": "Tür", "typ": "Ersatzteil", "bezeichnung": "Einsteckkassette Tür", "preis": 49.0, "einheit": "je Stück", "hinweis": ""},

    # Möbel
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Stapelstuhl", "preis": 35.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Rollcontainer", "preis": 158.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Spind", "preis": 189.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Tisch", "preis": 150.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Polsterstuhl", "preis": 39.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Sideboard", "preis": 249.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Aktenschrank", "preis": 316.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Drehstuhl", "preis": 98.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Ersatzteil", "bezeichnung": "Etagenbett", "preis": 249.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Entsorgung", "bezeichnung": "Möbelentsorgung", "preis": 59.0, "einheit": "je m³", "hinweis": ""},
    {"kategorie": "Möbel", "typ": "Entsorgung", "bezeichnung": "Matratzenentsorgung", "preis": 29.0, "einheit": "je Stück", "hinweis": ""},

    # Sanitär
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Bodenablaufgitter", "preis": 36.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Seifenhalter", "preis": 19.4, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Seifenspender", "preis": 45.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Armatur Waschbecken Einhebelmischer", "preis": 45.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Armatur Dusche Einhebelmischer Brause", "preis": 45.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Klobrille", "preis": 21.2, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Klobrille inkl. Montage", "preis": 35.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Toilettenschüssel", "preis": 119.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Duschstange", "preis": 25.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Duschkopfset inkl. Montage", "preis": 59.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Waschbecken", "preis": 149.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Mischbatterie", "preis": 68.5, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Urinalschüssel", "preis": 139.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Schamwand / Toilettenwand", "preis": 189.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Druckminderer", "preis": 192.0, "einheit": "je Stück", "hinweis": "zzgl. 3 Std. Montage"},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Schauglas Druckminderer", "preis": 25.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Urinal-Druckspüler", "preis": 65.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Falthandtuchspender", "preis": 39.9, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Spülkasten", "preis": 79.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Eckventil", "preis": 25.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Sanitär", "typ": "Ersatzteil", "bezeichnung": "Hauswasserwerk", "preis": 790.0, "einheit": "je Stück", "hinweis": "zzgl. 215€ An- und Abfahrt"},

    # Küche
    {"kategorie": "Küche", "typ": "Ersatzteil", "bezeichnung": "Miniküche komplett", "preis": 698.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Küche", "typ": "Ersatzteil", "bezeichnung": "Kühlschrank", "preis": 185.0, "einheit": "je Stück", "hinweis": ""},

    # Strom
    {"kategorie": "Strom", "typ": "Ersatzteil", "bezeichnung": "Steckdosenabdeckung", "preis": 7.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Strom", "typ": "Ersatzteil", "bezeichnung": "Steckdose", "preis": 15.9, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Strom", "typ": "Ersatzteil", "bezeichnung": "Lichtschalter", "preis": 28.8, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Strom", "typ": "Ersatzteil", "bezeichnung": "LED-Leuchtstoffröhre", "preis": 22.9, "einheit": "je Stück", "hinweis": "Universal"},
    {"kategorie": "Strom", "typ": "Ersatzteil", "bezeichnung": "LED-Lampe für Leuchtstoffröhren", "preis": 73.9, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Strom", "typ": "Ersatzteil", "bezeichnung": "FI-Schalter", "preis": 72.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Strom", "typ": "Ersatzteil", "bezeichnung": "Aufputzdose 32A männlich", "preis": 36.0, "einheit": "je Stück", "hinweis": ""},

    # Strom Sanitär
    {"kategorie": "Strom Sanitär", "typ": "Ersatzteil", "bezeichnung": "Heißwasserspeicher 5 ltr. Untertisch", "preis": 89.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Strom Sanitär", "typ": "Ersatzteil", "bezeichnung": "Durchlauferhitzer", "preis": 169.0, "einheit": "je Stück", "hinweis": ""},

    # Klimatisierung
    {"kategorie": "Klimatisierung", "typ": "Ersatzteil", "bezeichnung": "Lüfter", "preis": 78.5, "einheit": "je Stück", "hinweis": ""},

    # Rollo
    {"kategorie": "Rollo", "typ": "Ersatzteil", "bezeichnung": "Rollladenabdeckleiste inkl. Montage", "preis": 50.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Rollo", "typ": "Ersatzteil", "bezeichnung": "Rolladen 15x Lamellen", "preis": 180.0, "einheit": "je Stück", "hinweis": "á 12€ pro Lamelle"},
    {"kategorie": "Rollo", "typ": "Ersatzteil", "bezeichnung": "Rolladengurt", "preis": 19.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Rollo", "typ": "Ersatzteil", "bezeichnung": "Rollo-Kassette", "preis": 75.0, "einheit": "je Stück", "hinweis": ""},

    # Fenster
    {"kategorie": "Fenster", "typ": "Ersatzteil", "bezeichnung": "Fenster komplett inkl. Montage", "preis": 365.0, "einheit": "je Stück", "hinweis": "inkl. 2h Montage"},
    {"kategorie": "Fensterpaneele", "typ": "Ersatzteil", "bezeichnung": "Fensterpaneele komplett", "preis": 945.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Fensterflügel Klima", "typ": "Ersatzteil", "bezeichnung": "Fensterflügel Klima", "preis": 78.0, "einheit": "je Stück", "hinweis": ""},

    # Windfang / Paneel
    {"kategorie": "Windfang", "typ": "Ersatzteil", "bezeichnung": "Windfang komplett", "preis": 996.0, "einheit": "je Stück", "hinweis": ""},
    {"kategorie": "Paneel", "typ": "Ersatzteil", "bezeichnung": "Standardpaneel", "preis": 386.0, "einheit": "je Stück", "hinweis": ""},

    # Montage / Reinigung
    {"kategorie": "Montage", "typ": "Allgemein", "bezeichnung": "Montagestunde", "preis": 68.0, "einheit": "je Stunde", "hinweis": ""},
    {"kategorie": "Reinigung", "typ": "Allgemein", "bezeichnung": "Reinigungsstunde", "preis": 59.0, "einheit": "je Stunde", "hinweis": ""},
    {"kategorie": "Reinigung", "typ": "Nikotin", "bezeichnung": "Starke Nikotinverschmutzung", "preis": 110.0, "einheit": "je Reinigung", "hinweis": "nach Aufwand, ab"},
    {"kategorie": "Reinigung", "typ": "Graffiti", "bezeichnung": "Graffitientfernung / Außenputz", "preis": 59.0, "einheit": "je Stunde/m²", "hinweis": ""},
    {"kategorie": "Reinigung", "typ": "Klebereste", "bezeichnung": "Klebereste entfernen", "preis": 100.0, "einheit": "je Reinigung", "hinweis": ""},
    {"kategorie": "Reinigung", "typ": "Sonderreinigung", "bezeichnung": "Sonderreinigung", "preis": 125.0, "einheit": "je Reinigung", "hinweis": "ab"},
]

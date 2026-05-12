#!/usr/bin/env python3
"""
PST to Text Converter
Konvertiert eine Outlook PST-Datei in lesbare Textdateien.

Installation (einmalig):
  pip install pypff

Verwendung:
  python convert_pst_to_text.py backup.pst
  python convert_pst_to_text.py backup.pst --output ausgabe_ordner
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import pypff
except ImportError:
    print("Fehler: pypff nicht installiert.")
    print("Bitte installieren mit: pip install pypff")
    sys.exit(1)


def sanitize_filename(name: str, max_len: int = 80) -> str:
    """Entfernt unerlaubte Zeichen aus Dateinamen."""
    keep = set(' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_()')
    cleaned = ''.join(c if c in keep else '_' for c in name)
    return cleaned.strip()[:max_len] or 'unbekannt'


def get_message_text(message) -> str:
    """Extrahiert den Text aus einer Nachricht."""
    parts = []

    try:
        sender = message.sender_name or ''
        if sender:
            parts.append(f"Von:      {sender}")
    except Exception:
        pass

    try:
        sender_email = message.sender_email_address or ''
        if sender_email:
            parts.append(f"E-Mail:   {sender_email}")
    except Exception:
        pass

    try:
        subject = message.subject or '(kein Betreff)'
        parts.append(f"Betreff:  {subject}")
    except Exception:
        parts.append("Betreff:  (kein Betreff)")

    try:
        delivery_time = message.delivery_time
        if delivery_time:
            parts.append(f"Datum:    {delivery_time}")
    except Exception:
        pass

    try:
        body = message.plain_text_body
        if body:
            if isinstance(body, bytes):
                body = body.decode('utf-8', errors='replace')
            parts.append(f"\n{body.strip()}")
    except Exception:
        pass

    if len(parts) <= 3:
        try:
            body = message.html_body
            if body:
                if isinstance(body, bytes):
                    body = body.decode('utf-8', errors='replace')
                # Einfaches HTML-Stripping
                import re
                body = re.sub(r'<[^>]+>', ' ', body)
                body = re.sub(r'\s+', ' ', body).strip()
                parts.append(f"\n{body}")
        except Exception:
            pass

    return '\n'.join(parts)


def process_folder(pff_folder, output_dir: Path, folder_path: str, stats: dict):
    """Verarbeitet einen Ordner rekursiv."""
    folder_name = sanitize_filename(pff_folder.name or 'Unbenannt')
    current_path = folder_path + '/' + folder_name if folder_path else folder_name

    msg_count = pff_folder.number_of_messages
    if msg_count > 0:
        out_folder = output_dir / Path(*current_path.split('/'))
        out_folder.mkdir(parents=True, exist_ok=True)

        print(f"  Ordner: {current_path} ({msg_count} Nachrichten)")

        for i in range(msg_count):
            try:
                message = pff_folder.get_message(i)
                text = get_message_text(message)

                try:
                    subject = sanitize_filename(message.subject or f'nachricht_{i+1}')
                except Exception:
                    subject = f'nachricht_{i+1}'

                filename = f"{i+1:04d}_{subject}.txt"
                out_file = out_folder / filename

                out_file.write_text(text, encoding='utf-8')
                stats['messages'] += 1

            except Exception as e:
                stats['errors'] += 1
                print(f"    Fehler bei Nachricht {i}: {e}")

    # Unterordner verarbeiten
    for j in range(pff_folder.number_of_sub_folders):
        try:
            sub = pff_folder.get_sub_folder(j)
            process_folder(sub, output_dir, current_path, stats)
        except Exception as e:
            stats['errors'] += 1
            print(f"  Fehler bei Unterordner: {e}")


def convert_pst(pst_path: str, output_dir: str):
    pst_path = Path(pst_path)
    if not pst_path.exists():
        print(f"Fehler: Datei nicht gefunden: {pst_path}")
        sys.exit(1)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Öffne: {pst_path}")
    print(f"Ausgabe: {output_dir.resolve()}")
    print()

    pff_file = pypff.file()
    pff_file.open(str(pst_path))

    stats = {'messages': 0, 'errors': 0}
    start = datetime.now()

    try:
        root = pff_file.get_root_folder()
        for i in range(root.number_of_sub_folders):
            try:
                folder = root.get_sub_folder(i)
                process_folder(folder, output_dir, '', stats)
            except Exception as e:
                print(f"Fehler bei Hauptordner {i}: {e}")
                stats['errors'] += 1
    finally:
        pff_file.close()

    elapsed = (datetime.now() - start).total_seconds()
    print()
    print(f"Fertig in {elapsed:.1f}s")
    print(f"  Nachrichten konvertiert: {stats['messages']}")
    print(f"  Fehler:                  {stats['errors']}")
    print(f"  Ausgabe:                 {output_dir.resolve()}")


def main():
    parser = argparse.ArgumentParser(description='PST zu Text Konverter')
    parser.add_argument('pst_file', help='Pfad zur PST-Datei')
    parser.add_argument('--output', '-o', default='pst_ausgabe',
                        help='Ausgabeordner (Standard: pst_ausgabe)')
    args = parser.parse_args()
    convert_pst(args.pst_file, args.output)


if __name__ == '__main__':
    main()

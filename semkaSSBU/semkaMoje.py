#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skript pre analýzu diagnóz podľa MKCH-10 (21 kapitol)
1) Načíta Excel/CSV s dátami pacientov.
2) Extrahuje rok vyšetrenia.
3) Priradí každú diagnózu ku kapitole MKCH-10 podľa definovaných rozsahov kódov.
4) Vykreslí stacked bar chart ročného vývoja počtu prípadov po kapitolách.
5) Identifikuje kódy, ktoré nepatria do žiadnej kapitoly (možno zastarané alebo chybné).
"""

import os
import zipfile
import sys

import pandas as pd
import matplotlib.pyplot as plt

# ------------ Pomocná funkcia na načítanie XLSX / XLS / CSV ------------
def read_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.xlsx', '.xls'):
        try:
            # skúsiť moderný XLSX
            return pd.read_excel(path, engine='openpyxl')
        except (ValueError, zipfile.BadZipFile):
            # prípadne starší XLS
            try:
                import xlrd  # noqa: F401
            except ModuleNotFoundError:
                print("Chýba knižnica xlrd pre čítanie .xls – nainštalujte: pip install xlrd", file=sys.stderr)
                sys.exit(1)
            return pd.read_excel(path, engine='xlrd')
    elif ext == '.csv':
        return pd.read_csv(path)
    else:
        raise ValueError(f"Nepodporovaný formát: {ext}")

# ------------- Nastavenia vstupných súborov -------------
DATA_FILE = 'SSBU25_dataset.xls'         # alebo .xls / .csv
DATE_COL  = 'validovany vysledok'
CODE_COL  = 'diagnoza MKCH-10'

# ------------- 1) Načítanie dát pacientov -------------
df = read_table(DATA_FILE)

# Prevod na datetime, odstránenie nevalidných záznamov
df[DATE_COL] = pd.to_datetime(df[DATE_COL], dayfirst=True, errors='coerce')
df = df.dropna(subset=[DATE_COL, CODE_COL]).copy()
df['rok'] = df[DATE_COL].dt.year

# ------------- 2) Definícia 21 kapitol a ich kódových rozsahov -------------
chapters = [
    ("I.   Infekčné a parazitárne choroby",                   "A00", "B99"),
    ("II.  Nádory",                                           "C00", "D48"),
    ("III. Choroby krvi a imunitného systému",                "D50", "D89"),
    ("IV.  Endokrinné, nutričné a metabolické choroby",       "E00", "E90"),
    ("V.   Duševné poruchy a poruchy správania",              "F00", "F99"),
    ("VI.  Choroby nervového systému",                        "G00", "G99"),
    ("VII. Choroby oka a jeho adnexov",                       "H00", "H59"),
    ("VIII.Choroby ucha a hlávkového výbežku",                "H60", "H95"),
    ("IX.  Choroby obehovej sústavy",                         "I00", "I99"),
    ("X.   Choroby dýchacej sústavy",                         "J00", "J99"),
    ("XI.  Choroby tráviacej sústavy",                        "K00", "K93"),
    ("XII. Choroby kože a podkožného tkaniva",                "L00", "L99"),
    ("XIII.Choroby svalovo-kostrového aparátu a spojivového tkaniva", "M00", "M99"),
    ("XIV. Choroby močovej a pohlavnej sústavy",              "N00", "N99"),
    ("XV.  Tehotenstvo, pôrod a šestonedelie",                "O00", "O99"),
    ("XVI. Niektoré stavy vzniknuté v perinatálnom období",   "P00", "P96"),
    ("XVII.Vrozené malformácie, deformácie a chromozomálne abnormality", "Q00", "Q99"),
    ("XVIII.Príznaky a abnormálne nálezy",                    "R00", "R99"),
    ("XIX. Poranenia a otravy",                               "S00", "T98"),
    ("XX.  Vonkajšie príčiny chorobnosti a úmrtnosti",        "V01", "Y98"),
    ("XXI. Faktory ovplyvňujúce zdravotný stav",              "Z00", "Z99"),
]

def map_to_chapter(code: str) -> str:
    """
    Mapuje MKCH-10 kód (napr. 'K73.9' alebo 'A015') na jednu z 21 kapitol podľa rozsahu.
    Ak kód nespadá do žiadneho rozsahu, vráti 'Nezaradené'.
    """
    c = code.strip().upper().replace('.', '')
    if len(c) < 3 or not c[0].isalpha() or not c[1:3].isdigit():
        return "Nezaradené"
    letter, num = c[0], int(c[1:3])
    for name, start, end in chapters:
        s_let, s_num = start[0], int(start[1:])
        e_let, e_num = end[0], int(end[1:])
        # prípad, keď je rozsah v rámci jedného písmena
        if letter == s_let == e_let:
            if s_num <= num <= e_num:
                return name
        # písmeno na začiatku rozsahu
        elif letter == s_let and num >= s_num:
            return name
        # písmeno na konci rozsahu
        elif letter == e_let and num <= e_num:
            return name
        # písmeno medzi (napr. A..B, V..Y)
        elif ord(s_let) < ord(letter) < ord(e_let):
            return name
    return "Nezaradené"

# ------------- 3) Priradenie kapitoly -------------
df['kapitola'] = df[CODE_COL].astype(str).apply(map_to_chapter)

# ------------- 4) Trendová analýza -------------
pivot = (
    df
    .groupby(['rok', 'kapitola'])
    .size()
    .unstack(fill_value=0)
    .sort_index()
)

fig, ax = plt.subplots(figsize=(14, 8))
pivot.plot(kind='bar', stacked=True, ax=ax)

# Presunieme legendu doprava mimo grafu
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), title='Kapitola')

ax.set_title('Ročný vývoj počtu diagnóz podľa kapitol MKCH-10')
ax.set_xlabel('Rok')
ax.set_ylabel('Počet prípadov')
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
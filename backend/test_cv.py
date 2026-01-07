#!/usr/bin/env python
# -*- coding: utf-8 -*-

from extractors.extracteur import (
    extraire_nom_prenom, extraire_formations, 
    extraire_experiences, extraire_loisirs,
    extraire_dates, extraire_email, extraire_telephone, extraire_adresse
)

# Exemple de CV pour test - avec adresse près du nom
cv_test = """
Jean Dupont
123 rue de Paris, 75001 Paris
Téléphone: 06 12 34 56 78
Email: jean.dupont@gmail.com

FORMATION
Master en Informatique - Université de Paris
2020 - 2022

Licence en Informatique - Université de Lyon
2017 - 2020

BTS en Systèmes Numériques - Institut Technique
2015 - 2017

EXPÉRIENCE PROFESSIONNELLE
Développeur Senior - Sopra Steria
Janvier 2022 - Présent
Responsable du développement des APIs

Développeur Full Stack - Accenture
Mars 2020 - Décembre 2021
Développement d'applications web

Développeur Junior - Orange
Juin 2019 - Février 2020
Maintenance du code legacy

LOISIRS
Programmation, Football, Lecture, Photographie, Voyage
"""

print("=" * 50)
print("RÉSULTATS EXTRACTION CV")
print("=" * 50)

nom = extraire_nom_prenom(cv_test)
print(f"\n✓ Nom/Prénom: {nom}")

formations = extraire_formations(cv_test)
print(f"\n✓ Formations ({len(formations)}):")
for f in formations:
    print(f"  - {f}")

experiences = extraire_experiences(cv_test)
print(f"\n✓ Expériences ({len(experiences)}):")
for e in experiences:
    print(f"  - {e}")

loisirs = extraire_loisirs(cv_test)
print(f"\n✓ Loisirs ({len(loisirs)}):")
for l in loisirs:
    print(f"  - {l}")

dates = extraire_dates(cv_test)
print(f"\n✓ Dates ({len(dates)}):")
for d in dates:
    print(f"  - {d}")

emails = extraire_email(cv_test)
print(f"\n✓ Emails ({len(emails)}):")
for e in emails:
    print(f"  - {e}")

telephones = extraire_telephone(cv_test)
print(f"\n✓ Téléphones ({len(telephones)}):")
for t in telephones:
    print(f"  - {t}")

adresses = extraire_adresse(cv_test)
print(f"\n✓ Adresses ({len(adresses)}):")
for a in adresses:
    print(f"  - {a}")

print("\n" + "=" * 50)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from extractors.extracteur import extraire_nom_prenom

# Test 1: CV normal
cv1 = """
Jean Dupont
123 rue de Paris, 75001 Paris
Téléphone: 06 12 34 56 78
"""

# Test 2: Adresse avant nom (mauvais format)
cv2 = """
123 rue de Paris, 75001 Paris
Jean Dupont
Téléphone: 06 12 34 56 78
"""

# Test 3: Adresse complexe en première ligne
cv3 = """
Pierre Bourdan, 45 avenue des Champs, 75008 Paris
Email: pierre@gmail.com
"""

# Test 4: Nom avec tiret
cv4 = """
Marie-Claire Legrand
75001 Paris
"""

# Test 5: Plusieurs mots (à rejeter)
cv5 = """
Chef de Projet Développement
123 rue Paris
"""

# Test 6: Nom avec accents
cv6 = """
François Érique Müller
12 rue Saint-Paul
"""

tests = [
    ("CV Normal", cv1, "Jean Dupont"),
    ("Adresse avant nom", cv2, "Jean Dupont"),
    ("Adresse complexe", cv3, None),  # Doit rejeter car contient "avenue"
    ("Nom avec tiret", cv4, "Marie-Claire Legrand"),
    ("Plusieurs mots", cv5, None),  # Doit rejeter
    ("Accents", cv6, "François Érique Müller"),
]

print("=" * 60)
print("TEST EXTRACTION NOM/PRÉNOM")
print("=" * 60)

for nom_test, cv, attendu in tests:
    resultat = extraire_nom_prenom(cv)
    statut = "✓" if resultat == attendu else "✗"
    print(f"\n{statut} {nom_test}")
    print(f"  Attendu:  {attendu}")
    print(f"  Obtenu:   {resultat}")
    if resultat != attendu:
        print(f"  ⚠️  ERREUR")

print("\n" + "=" * 60)

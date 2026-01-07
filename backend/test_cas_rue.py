#!/usr/bin/env python
# -*- coding: utf-8 -*-

from extractors.extracteur import extraire_nom_prenom

# Test avec le cas EXACT de l'utilisateur
cv_probleme_exact = """
│ 👤 Nom            │ Pierre Bourdan                                                                                                   │
│ 📧 Email          │ adele.patarot@etu.imt-nord-europe.fr                                                                          │
│ 📞 Téléphone      │ 06 18 36 54 44                                                                                                   │
│ 🏠 Adresse        │ 21, rue Pierre Bourdan, 78160 Marly-le-Roi
"""

# Test 2: CV format simple avec même problème
cv_probleme_simple = """
Pierre Bourdan
Email: adele.patarot@etu.imt-nord-europe.fr
Téléphone: 06 18 36 54 44
Adresse: 21, rue Pierre Bourdan, 78160 Marly-le-Roi
"""

# Test 3: CV correct où le nom ne doit pas être confondu
cv_correct = """
Adele Patarot
Email: adele.patarot@etu.imt-nord-europe.fr
Adresse: 21, rue Pierre Bourdan, 78160 Marly-le-Roi
"""

# Test 4: Juste l'adresse, pas de nom valide
cv_adresse_seule = """
21, rue Pierre Bourdan, 78160 Marly-le-Roi
Email: adele.patarot@etu.imt-nord-europe.fr
"""

tests = [
    ("Cas EXACT utilisateur (Pierre Bourdan dans adresse)", cv_probleme_exact, "Adele Patarot"),
    ("CV simple (Pierre Bourdan = nom rue)", cv_probleme_simple, "Adele Patarot"),
    ("CV correct (Adele Patarot au début)", cv_correct, "Adele Patarot"),
    ("Adresse seule (extraction depuis email)", cv_adresse_seule, "Adele Patarot"),
]

print("=" * 70)
print("TEST EXTRACTION NOM/PRÉNOM - Vérification croisée avec adresse")
print("=" * 70)

for nom_test, cv, attendu in tests:
    resultat = extraire_nom_prenom(cv)
    statut = "✓" if resultat == attendu else "✗"
    print(f"\n{statut} {nom_test}")
    print(f"  Attendu:  {attendu}")
    print(f"  Obtenu:   {resultat}")
    if resultat != attendu:
        print(f"  ⚠️  ERREUR")

print("\n" + "=" * 70)

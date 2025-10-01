# Ajout du chemin pour l'import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de nos fonctions d'extraction
from backend.extractors.extracteur import extraire_dates, extraire_email, extraire_telephone

# Test d'extraction de dates
print("\n=== Test des dates ===")
texte = "J'ai commencé le 01/09/2023 et fini le 31/12/2024"
dates = extraire_dates(texte)
print(f"Texte: {texte}")
print(f"Dates trouvées: {dates}")

# Test d'extraction d'emails
print("\n=== Test des emails ===")
texte = "Contactez-moi à john.doe@gmail.com ou jane@example.com"
emails = extraire_email(texte)
print(f"Texte: {texte}")
print(f"Emails trouvés: {emails}")

# Test d'extraction de numéros de téléphone
print("\n=== Test des numéros de téléphone ===")
texte = "Appelez-moi au 06.12.34.56.78 ou au 01 23 45 67 89"
telephones = extraire_telephone(texte)
print(f"Texte: {texte}")
print(f"Numéros trouvés: {telephones}")

# Test avec votre propre texte
print("\n=== Test avec votre texte ===")
votre_texte = """
Mettez ici le texte que vous voulez tester.
Par exemple : Mon email est test@test.fr, 
je suis né le 15/03/1990 et mon téléphone est le 07.11.22.33.44
"""
print("Dates:", extraire_dates(votre_texte))
print("Emails:", extraire_email(votre_texte))
print("Téléphones:", extraire_telephone(votre_texte))
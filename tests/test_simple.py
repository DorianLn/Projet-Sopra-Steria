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
Je suis disponible de Mars 2024 à Décembre 2025.
Mon stage s'est déroulé de 06/2023 à 12/2023.
Période : 2021-2023

J'habite au 123 rue de la Paix, 75001 Paris
Vous pouvez aussi me contacter à Lyon (69)
Mon email est test@test.fr
Téléphone : 07.11.22.33.44
"""
print("Dates trouvées:", extraire_dates(votre_texte))
print("Emails trouvés:", extraire_email(votre_texte))
print("Téléphones trouvés:", extraire_telephone(votre_texte))
print("Adresses trouvées:", extraire_adresse(votre_texte))
import os
from docx import Document
from extractors.section_classifier import extraire_par_sections


def lire_docx(chemin):
    doc = Document(chemin)
    return "\n".join([p.text for p in doc.paragraphs])


def tester_un_cv(chemin):
    print("\n" + "=" * 80)
    print(f"📄 TEST DU CV : {os.path.basename(chemin)}")
    print("=" * 80)

    texte = lire_docx(chemin)

    sections = extraire_par_sections(texte)

    for nom, contenu in sections.items():
        print(f"\n🔹 SECTION : {nom}")
        print("-" * 60)

        lignes = contenu.strip().split("\n")

        if not lignes or lignes == ['']:
            print("⚠️  Section vide")
        else:
            print("\n".join(lignes[:10]))

            if len(lignes) > 10:
                print("... (tronqué)")

    print("\n" + "=" * 80 + "\n")


def tester_tous_les_cv(dossier):
    fichiers = [f for f in os.listdir(dossier) if f.endswith(".docx")]

    if not fichiers:
        print("Aucun fichier docx trouvé")
        return

    for fichier in fichiers:
        chemin = os.path.join(dossier, fichier)
        tester_un_cv(chemin)


if __name__ == "__main__":
    DOSSIER_TEST = "data/input"
    tester_tous_les_cv(DOSSIER_TEST)

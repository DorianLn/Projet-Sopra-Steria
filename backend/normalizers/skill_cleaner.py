import re

TECH_KEYWORDS = {
    "java", "python", "javascript", "typescript", "c++", "c#", "php",
    "spring", "spring boot", "react", "angular", "vue", "django",
    "flask", "node", "nodejs", "kafka", "docker", "kubernetes",
    "jenkins", "git", "sql", "mysql", "postgresql", "oracle",
    "mongodb", "elasticsearch", "hibernate", "rest", "api",
    "aws", "azure", "gcp", "linux", "bash"
}

FONCTIONNEL_KEYWORDS = {
    "agile", "scrum", "safe", "gestion", "management",
    "pilotage", "kpi", "communication", "organisation",
    "analyse", "méthodologie", "client", "projet",
    "recueil du besoin", "spécifications",
    "animation", "coordination", "encadrement"
}

NOISE_PATTERNS = [
    r"connaissance des",
    r"maîtrise de",
    r"expérience en",
    r"outils\s*:",
    r"environnement\s*:",
    r"méthodologies\s*:",
    r"langages\s*&?\s*frameworks",
    r"programmation\s*:",
    r"devops\s*&?\s*ci/cd",
    r"messaging\s*&?\s*data"
]


def nettoyer_texte(texte: str) -> str:
    t = texte.lower().strip()

    for pattern in NOISE_PATTERNS:
        t = re.sub(pattern, "", t)

    t = re.sub(r"[•❖:]", "", t)
    t = re.sub(r"\s+", " ", t)

    return t.strip()


def detecter_type_competence(comp: str) -> str:
    comp_lower = comp.lower()

    if any(k in comp_lower for k in TECH_KEYWORDS):
        return "technique"

    if any(k in comp_lower for k in FONCTIONNEL_KEYWORDS):
        return "fonctionnelle"

    return "inconnu"


def nettoyer_competence_unitaire(comp: str) -> str:
    comp = nettoyer_texte(comp)

    comp = comp.replace("java (8 –21)", "java")
    comp = comp.replace("post", "postgresql")

    comp = comp.strip(" .-")

    return comp.strip()


def nettoyer_competences_json(competences: dict) -> dict:
    """
    Prend en entrée la structure produite par separer_competences
    et renvoie une version nettoyée
    """

    propres = {
        "techniques": {
            "programmation": [],
            "frameworks": [],
            "bases_de_donnees": [],
            "devops_cloud": [],
            "outils": [],
            "autres": []
        },
        "fonctionnelles": []
    }

    tech = competences.get("techniques", {})

    for categorie, liste in tech.items():
        for comp in liste:
            c = nettoyer_competence_unitaire(comp)

            if len(c) < 2:
                continue

            propres["techniques"][categorie].append(c)

    for comp in competences.get("fonctionnelles", []):
        c = nettoyer_competence_unitaire(comp)

        if len(c) < 2:
            continue

        propres["fonctionnelles"].append(c)

    for cat in propres["techniques"]:
        propres["techniques"][cat] = list(dict.fromkeys(propres["techniques"][cat]))

    propres["fonctionnelles"] = list(dict.fromkeys(propres["fonctionnelles"]))

    return propres

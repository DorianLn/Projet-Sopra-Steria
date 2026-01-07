"""
Données d'entraînement annotées pour le NER spaCy spécialisé CV.

Entités personnalisées:
- PERSON_NAME: Nom complet du candidat
- COMPANY: Nom d'entreprise
- SCHOOL: Établissement d'enseignement
- DIPLOMA: Diplôme ou certification
- JOB_TITLE: Intitulé de poste
- SKILL: Compétence technique ou soft skill
- LANGUAGE: Langue parlée
- DATE_RANGE: Période (ex: 2020-2023)
- LOCATION: Lieu/Adresse

Format: (texte, {"entities": [(start, end, label), ...]})
"""

# =============================================================================
# DONNÉES D'ENTRAÎNEMENT NER
# =============================================================================

NER_TRAINING_DATA = [
    # === NOMS DE PERSONNES ===
    (
        "Marie DUPONT",
        {"entities": [(0, 12, "PERSON_NAME")]}
    ),
    (
        "Jean-Pierre MARTIN",
        {"entities": [(0, 18, "PERSON_NAME")]}
    ),
    (
        "Léo WEBER",
        {"entities": [(0, 9, "PERSON_NAME")]}
    ),
    (
        "Adèle PATAROT",
        {"entities": [(0, 13, "PERSON_NAME")]}
    ),
    (
        "Pierre Bourdan",
        {"entities": [(0, 14, "PERSON_NAME")]}
    ),
    (
        "Sophie LEMAIRE",
        {"entities": [(0, 14, "PERSON_NAME")]}
    ),
    (
        "François-Xavier DURAND",
        {"entities": [(0, 22, "PERSON_NAME")]}
    ),
    (
        "Émilie BERNARD",
        {"entities": [(0, 14, "PERSON_NAME")]}
    ),
    (
        "Alexandre PETIT",
        {"entities": [(0, 15, "PERSON_NAME")]}
    ),
    (
        "Thomas LEROY",
        {"entities": [(0, 12, "PERSON_NAME")]}
    ),
    
    # === FORMATIONS ===
    (
        "Master Informatique",
        {"entities": [(0, 19, "DIPLOMA")]}
    ),
    (
        "Université Paris-Saclay",
        {"entities": [(0, 23, "SCHOOL")]}
    ),
    (
        "École Polytechnique Paris",
        {"entities": [(0, 25, "SCHOOL")]}
    ),
    (
        "IMT Nord Europe",
        {"entities": [(0, 15, "SCHOOL")]}
    ),
    (
        "Licence Informatique",
        {"entities": [(0, 20, "DIPLOMA")]}
    ),
    (
        "Master Data Science",
        {"entities": [(0, 19, "DIPLOMA")]}
    ),
    (
        "BTS SIO option SLAM",
        {"entities": [(0, 19, "DIPLOMA")]}
    ),
    (
        "Doctorat en Intelligence Artificielle",
        {"entities": [(0, 37, "DIPLOMA")]}
    ),
    (
        "Université de Lyon",
        {"entities": [(0, 18, "SCHOOL")]}
    ),
    (
        "Université Pierre et Marie Curie",
        {"entities": [(0, 32, "SCHOOL")]}
    ),
    
    # === EXPÉRIENCES PROFESSIONNELLES ===
    (
        "Lead DevOps",
        {"entities": [(0, 11, "JOB_TITLE")]}
    ),
    (
        "Amazon Web Services",
        {"entities": [(0, 19, "COMPANY")]}
    ),
    (
        "Développeur Python Senior",
        {"entities": [(0, 25, "JOB_TITLE")]}
    ),
    (
        "Google",
        {"entities": [(0, 6, "COMPANY")]}
    ),
    (
        "Capgemini",
        {"entities": [(0, 9, "COMPANY")]}
    ),
    (
        "Sopra Steria",
        {"entities": [(0, 12, "COMPANY")]}
    ),
    (
        "Consultant IT",
        {"entities": [(0, 13, "JOB_TITLE")]}
    ),
    (
        "Chef de Projet Digital",
        {"entities": [(0, 22, "JOB_TITLE")]}
    ),
    (
        "Accenture",
        {"entities": [(0, 9, "COMPANY")]}
    ),
    (
        "Business Analyst Junior",
        {"entities": [(0, 23, "JOB_TITLE")]}
    ),
    (
        "BNP Paribas",
        {"entities": [(0, 11, "COMPANY")]}
    ),
    (
        "Microsoft",
        {"entities": [(0, 9, "COMPANY")]}
    ),
    (
        "Software Engineer",
        {"entities": [(0, 17, "JOB_TITLE")]}
    ),
    (
        "Ingénieur DevOps",
        {"entities": [(0, 16, "JOB_TITLE")]}
    ),
    (
        "Data Scientist",
        {"entities": [(0, 14, "JOB_TITLE")]}
    ),
    (
        "Développeur Full Stack",
        {"entities": [(0, 22, "JOB_TITLE")]}
    ),
    
    # === DATES ===
    (
        "2018-2020",
        {"entities": [(0, 9, "DATE_RANGE")]}
    ),
    (
        "2020-2023",
        {"entities": [(0, 9, "DATE_RANGE")]}
    ),
    (
        "Janvier 2021 - Présent",
        {"entities": [(0, 22, "DATE_RANGE")]}
    ),
    (
        "Mars 2019 - Décembre 2022",
        {"entities": [(0, 25, "DATE_RANGE")]}
    ),
    (
        "2019-2021",
        {"entities": [(0, 9, "DATE_RANGE")]}
    ),
    
    # === COMPÉTENCES ===
    (
        "Python",
        {"entities": [(0, 6, "SKILL")]}
    ),
    (
        "Java",
        {"entities": [(0, 4, "SKILL")]}
    ),
    (
        "JavaScript",
        {"entities": [(0, 10, "SKILL")]}
    ),
    (
        "Docker",
        {"entities": [(0, 6, "SKILL")]}
    ),
    (
        "Kubernetes",
        {"entities": [(0, 10, "SKILL")]}
    ),
    (
        "AWS",
        {"entities": [(0, 3, "SKILL")]}
    ),
    (
        "React",
        {"entities": [(0, 5, "SKILL")]}
    ),
    (
        "Terraform",
        {"entities": [(0, 9, "SKILL")]}
    ),
    
    # === LANGUES ===
    (
        "Français natif",
        {"entities": [(0, 8, "LANGUAGE")]}
    ),
    (
        "Anglais courant",
        {"entities": [(0, 7, "LANGUAGE")]}
    ),
    (
        "Espagnol intermédiaire",
        {"entities": [(0, 8, "LANGUAGE")]}
    ),
    (
        "Allemand notions",
        {"entities": [(0, 8, "LANGUAGE")]}
    ),
    
    # === ADRESSES ET LIEUX ===
    (
        "Paris",
        {"entities": [(0, 5, "LOCATION")]}
    ),
    (
        "Lyon",
        {"entities": [(0, 4, "LOCATION")]}
    ),
    (
        "75001 Paris",
        {"entities": [(0, 11, "LOCATION")]}
    ),
    (
        "12 rue des Lilas",
        {"entities": [(0, 16, "LOCATION")]}
    ),
    
    # === EXEMPLES COMBINÉS SIMPLES ===
    (
        "Marie DUPONT - Développeuse Python",
        {"entities": [(0, 12, "PERSON_NAME"), (15, 34, "JOB_TITLE")]}
    ),
    (
        "Développeur chez Google",
        {"entities": [(0, 11, "JOB_TITLE"), (17, 23, "COMPANY")]}
    ),
    (
        "Master à Polytechnique",
        {"entities": [(0, 6, "DIPLOMA"), (10, 22, "SCHOOL")]}
    ),
    (
        "Stage chez Capgemini",
        {"entities": [(0, 5, "JOB_TITLE"), (11, 20, "COMPANY")]}
    ),
    (
        "Consultant chez Sopra Steria",
        {"entities": [(0, 10, "JOB_TITLE"), (16, 28, "COMPANY")]}
    ),
    
    # === EXEMPLES CONTEXTUELS FORMATIONS ===
    (
        "2018-2020: Master Informatique à l'Université Paris-Saclay",
        {"entities": [(0, 9, "DATE_RANGE"), (11, 30, "DIPLOMA"), (35, 58, "SCHOOL")]}
    ),
    (
        "Diplôme d'Ingénieur - IMT Nord Europe (2019-2024)",
        {"entities": [(0, 18, "DIPLOMA"), (22, 37, "SCHOOL"), (39, 48, "DATE_RANGE")]}
    ),
    (
        "2015-2018: Licence Mathématiques - Université de Lyon",
        {"entities": [(0, 9, "DATE_RANGE"), (11, 33, "DIPLOMA"), (36, 53, "SCHOOL")]}
    ),
    (
        "Master Data Science, École Polytechnique, 2019-2021",
        {"entities": [(0, 18, "DIPLOMA"), (21, 40, "SCHOOL"), (42, 51, "DATE_RANGE")]}
    ),
    (
        "Baccalauréat S mention Très Bien - Lycée Hoche (2018)",
        {"entities": [(0, 32, "DIPLOMA"), (35, 46, "SCHOOL"), (48, 52, "DATE_RANGE")]}
    ),
    (
        "EPITA - Cycle Ingénieur Informatique (2020-2025)",
        {"entities": [(0, 5, "SCHOOL"), (8, 35, "DIPLOMA"), (37, 46, "DATE_RANGE")]}
    ),
    (
        "Formation en alternance: Master MIAGE à Paris-Dauphine",
        {"entities": [(25, 37, "DIPLOMA"), (41, 54, "SCHOOL")]}
    ),
    (
        "BTS SIO option SLAM - Lycée Chaptal, Paris (2017-2019)",
        {"entities": [(0, 19, "DIPLOMA"), (22, 35, "SCHOOL"), (44, 53, "DATE_RANGE")]}
    ),
    (
        "Doctorat en Intelligence Artificielle - Inria, Université Grenoble Alpes",
        {"entities": [(0, 37, "DIPLOMA"), (40, 44, "SCHOOL"), (46, 72, "SCHOOL")]}
    ),
    (
        "DUT Informatique à l'IUT de Montreuil (2015-2017)",
        {"entities": [(0, 15, "DIPLOMA"), (21, 37, "SCHOOL"), (39, 48, "DATE_RANGE")]}
    ),
    
    # === EXEMPLES CONTEXTUELS EXPÉRIENCES ===
    (
        "2021-Présent: Lead DevOps chez Amazon Web Services, Paris",
        {"entities": [(0, 12, "DATE_RANGE"), (14, 24, "JOB_TITLE"), (30, 49, "COMPANY"), (51, 56, "LOCATION")]}
    ),
    (
        "Développeur Python Senior - Google (2019-2022)",
        {"entities": [(0, 25, "JOB_TITLE"), (28, 34, "COMPANY"), (36, 45, "DATE_RANGE")]}
    ),
    (
        "Consultant IT chez Capgemini de 2018 à 2021",
        {"entities": [(0, 12, "JOB_TITLE"), (18, 27, "COMPANY")]}
    ),
    (
        "Ingénieur DevOps - Thales, Bordeaux (Janvier 2020 - Décembre 2022)",
        {"entities": [(0, 15, "JOB_TITLE"), (18, 24, "COMPANY"), (26, 34, "LOCATION"), (36, 65, "DATE_RANGE")]}
    ),
    (
        "Stagiaire Développeur Web chez Orange (6 mois, 2019)",
        {"entities": [(0, 24, "JOB_TITLE"), (30, 36, "COMPANY")]}
    ),
    (
        "Chef de Projet Digital - BNP Paribas, Paris (2017-2020)",
        {"entities": [(0, 22, "JOB_TITLE"), (25, 35, "COMPANY"), (37, 42, "LOCATION"), (44, 53, "DATE_RANGE")]}
    ),
    (
        "Data Scientist Junior - Société Générale (2020-2022)",
        {"entities": [(0, 20, "JOB_TITLE"), (23, 40, "COMPANY"), (42, 51, "DATE_RANGE")]}
    ),
    (
        "Alternance: Développeur Full Stack chez Sopra Steria (2019-2021)",
        {"entities": [(12, 33, "JOB_TITLE"), (39, 51, "COMPANY"), (53, 62, "DATE_RANGE")]}
    ),
    (
        "Product Owner - Airbus Defence & Space, Toulouse (2018-Présent)",
        {"entities": [(0, 13, "JOB_TITLE"), (16, 38, "COMPANY"), (40, 48, "LOCATION"), (50, 62, "DATE_RANGE")]}
    ),
    (
        "Architecte Cloud AWS - Accenture Technology (2021-2023)",
        {"entities": [(0, 19, "JOB_TITLE"), (22, 43, "COMPANY"), (45, 54, "DATE_RANGE")]}
    ),
    (
        "Business Analyst - Inetum, Lyon (Mars 2019 - Août 2021)",
        {"entities": [(0, 16, "JOB_TITLE"), (19, 25, "COMPANY"), (27, 31, "LOCATION"), (33, 54, "DATE_RANGE")]}
    ),
    (
        "Scrum Master chez Atos Origin (2017-2019)",
        {"entities": [(0, 11, "JOB_TITLE"), (17, 28, "COMPANY"), (30, 39, "DATE_RANGE")]}
    ),
    
    # === EXEMPLES DE LIGNES DE CV RÉELLES ===
    (
        "FORMATIONS",
        {"entities": []}
    ),
    (
        "EXPÉRIENCES PROFESSIONNELLES",
        {"entities": []}
    ),
    (
        "COMPÉTENCES TECHNIQUES",
        {"entities": []}
    ),
    (
        "LANGUES",
        {"entities": []}
    ),
    (
        "Septembre 2020 - Août 2023: Ingénieur d'études chez CGI, Nantes",
        {"entities": [(0, 26, "DATE_RANGE"), (28, 46, "JOB_TITLE"), (52, 55, "COMPANY"), (57, 63, "LOCATION")]}
    ),
    (
        "2022 – 2024: École Centrale de Lyon, Master Génie Industriel",
        {"entities": [(0, 11, "DATE_RANGE"), (13, 35, "SCHOOL"), (37, 60, "DIPLOMA")]}
    ),
    (
        "S2 2023: Stage Développeur Backend - Ubisoft, Montpellier",
        {"entities": [(0, 7, "DATE_RANGE"), (9, 33, "JOB_TITLE"), (36, 43, "COMPANY"), (45, 56, "LOCATION")]}
    ),
    
    # === EXEMPLES ENRICHIS FORMATIONS (patterns variés) ===
    (
        "EPITA : Dernière année du cycle ingénieur (Kremlin-Bicêtre)",
        {"entities": [(0, 5, "SCHOOL"), (8, 40, "DIPLOMA"), (42, 57, "LOCATION")]}
    ),
    (
        "Lycée Hoche : Baccalauréat S mention assez bien (Versailles)",
        {"entities": [(0, 11, "SCHOOL"), (14, 46, "DIPLOMA"), (48, 58, "LOCATION")]}
    ),
    (
        "Rhine-Waal University : Programme Data Science (Allemagne)",
        {"entities": [(0, 20, "SCHOOL"), (23, 45, "DIPLOMA"), (47, 56, "LOCATION")]}
    ),
    (
        "2020-2022: Master MIAGE - Université Paris-Dauphine",
        {"entities": [(0, 9, "DATE_RANGE"), (11, 23, "DIPLOMA"), (26, 51, "SCHOOL")]}
    ),
    (
        "Prépa MPSI/MP* - Lycée Louis-le-Grand (2016-2018)",
        {"entities": [(0, 13, "DIPLOMA"), (16, 36, "SCHOOL"), (38, 47, "DATE_RANGE")]}
    ),
    (
        "Ingénieur spécialité Informatique - ISEP Paris (2018-2023)",
        {"entities": [(0, 33, "DIPLOMA"), (36, 46, "SCHOOL"), (48, 57, "DATE_RANGE")]}
    ),
    (
        "MBA Management des SI - HEC Paris (2021-2022)",
        {"entities": [(0, 20, "DIPLOMA"), (23, 32, "SCHOOL"), (34, 43, "DATE_RANGE")]}
    ),
    (
        "Certification Google Cloud Professional Data Engineer",
        {"entities": [(0, 53, "DIPLOMA")]}
    ),
    (
        "Formation continue Python avancé - OpenClassrooms (2023)",
        {"entities": [(0, 31, "DIPLOMA"), (34, 48, "SCHOOL"), (50, 54, "DATE_RANGE")]}
    ),
    (
        "Bootcamp Data Science - Le Wagon Paris (3 mois, 2022)",
        {"entities": [(0, 20, "DIPLOMA"), (23, 38, "SCHOOL")]}
    ),
    
    # === EXEMPLES ENRICHIS EXPÉRIENCES (patterns variés) ===
    (
        "S3 2024 – 2025 Rhine-Waal University, Allemagne",
        {"entities": [(0, 14, "DATE_RANGE"), (15, 35, "COMPANY"), (37, 46, "LOCATION")]}
    ),
    (
        "S2 2023 Paris - Stage de 18 semaines chez I NETUM en tant que développeur ABAP",
        {"entities": [(0, 7, "DATE_RANGE"), (8, 13, "LOCATION"), (42, 49, "COMPANY"), (62, 78, "JOB_TITLE")]}
    ),
    (
        "Stage 6 mois chez Thales - Développeur C++ embarqué",
        {"entities": [(0, 11, "JOB_TITLE"), (17, 23, "COMPANY"), (26, 51, "JOB_TITLE")]}
    ),
    (
        "Alternance 2 ans - Ingénieur Cloud AWS chez Orange Business",
        {"entities": [(0, 15, "DATE_RANGE"), (18, 36, "JOB_TITLE"), (42, 58, "COMPANY")]}
    ),
    (
        "Freelance Développeur React/Node.js (2022-Présent)",
        {"entities": [(0, 8, "JOB_TITLE"), (9, 34, "JOB_TITLE"), (36, 48, "DATE_RANGE")]}
    ),
    (
        "CDI - Architecte Solution Cloud - Atos (depuis 2021)",
        {"entities": [(6, 30, "JOB_TITLE"), (33, 37, "COMPANY"), (39, 51, "DATE_RANGE")]}
    ),
    (
        "Mission consulting 6 mois - Société Générale - Data Analyst",
        {"entities": [(0, 25, "DATE_RANGE"), (28, 44, "COMPANY"), (47, 59, "JOB_TITLE")]}
    ),
    (
        "Développeur Full Stack Java/Angular - CGI France (Nantes)",
        {"entities": [(0, 35, "JOB_TITLE"), (38, 48, "COMPANY"), (50, 56, "LOCATION")]}
    ),
    (
        "Tech Lead Python - Startup FinTech (2020-2023, Lyon)",
        {"entities": [(0, 16, "JOB_TITLE"), (19, 34, "COMPANY"), (36, 45, "DATE_RANGE"), (47, 51, "LOCATION")]}
    ),
    (
        "DevOps Engineer - AWS Partner Company - Remote (2022-Present)",
        {"entities": [(0, 15, "JOB_TITLE"), (18, 37, "COMPANY"), (47, 60, "DATE_RANGE")]}
    ),
    
    # === EXEMPLES DATES VARIÉES ===
    (
        "Septembre 2019 - Juin 2022",
        {"entities": [(0, 26, "DATE_RANGE")]}
    ),
    (
        "depuis janvier 2023",
        {"entities": [(0, 19, "DATE_RANGE")]}
    ),
    (
        "Oct. 2020 – Déc. 2021",
        {"entities": [(0, 21, "DATE_RANGE")]}
    ),
    (
        "S1 2024",
        {"entities": [(0, 7, "DATE_RANGE")]}
    ),
    (
        "3 ans (2019-2022)",
        {"entities": [(0, 17, "DATE_RANGE")]}
    ),
    (
        "2ème semestre 2023",
        {"entities": [(0, 18, "DATE_RANGE")]}
    ),
    (
        "Janvier - Mars 2024",
        {"entities": [(0, 19, "DATE_RANGE")]}
    ),
    
    # === EXEMPLES COMPÉTENCES ENRICHIS ===
    (
        "Machine Learning et Deep Learning",
        {"entities": [(0, 16, "SKILL"), (20, 33, "SKILL")]}
    ),
    (
        "CI/CD avec Jenkins et GitLab CI",
        {"entities": [(0, 5, "SKILL"), (11, 18, "SKILL"), (22, 31, "SKILL")]}
    ),
    (
        "Méthodologies Agile Scrum et Kanban",
        {"entities": [(14, 24, "SKILL"), (28, 34, "SKILL")]}
    ),
    (
        "Base de données: PostgreSQL, MongoDB, Redis",
        {"entities": [(17, 27, "SKILL"), (29, 36, "SKILL"), (38, 43, "SKILL")]}
    ),
    (
        "Cloud: AWS, GCP, Azure",
        {"entities": [(7, 10, "SKILL"), (12, 15, "SKILL"), (17, 22, "SKILL")]}
    ),
    (
        "Spring Boot, Hibernate, JPA",
        {"entities": [(0, 11, "SKILL"), (13, 22, "SKILL"), (24, 27, "SKILL")]}
    ),
    (
        "TensorFlow, PyTorch, Keras, scikit-learn",
        {"entities": [(0, 10, "SKILL"), (12, 19, "SKILL"), (21, 26, "SKILL"), (28, 40, "SKILL")]}
    ),
]

# =============================================================================
# DONNÉES D'ENTRAÎNEMENT TEXTCAT (Classification de sections)
# =============================================================================

SECTION_CATEGORIES = [
    "HEADER",           # En-tête avec nom/contact
    "PROFILE",          # Résumé/Objectif professionnel
    "EDUCATION",        # Formations
    "EXPERIENCE",       # Expériences professionnelles
    "SKILLS",           # Compétences
    "LANGUAGES",        # Langues
    "PROJECTS",         # Projets
    "CERTIFICATIONS",   # Certifications
    "INTERESTS",        # Loisirs/Intérêts
    "OTHER"             # Autre
]

TEXTCAT_TRAINING_DATA = [
    # === HEADER (en-tête avec nom/contact) ===
    ("Marie DUPONT\n06 12 34 56 78\nmarie.dupont@gmail.com\nParis, France", 
     {"cats": {"HEADER": 1.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Jean-Pierre MARTIN\nIngénieur DevOps\n+33 6 98 76 54 32\njp.martin@company.fr",
     {"cats": {"HEADER": 1.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Léo WEBER\nleo.weber@epita.fr\n+33 (6) 73 93 70\n78150 Le Chesnay",
     {"cats": {"HEADER": 1.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Sophie BERNARD - Développeuse Full Stack\n06 78 90 12 34\nsophie.bernard@gmail.com\nLyon",
     {"cats": {"HEADER": 1.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === PROFILE (résumé/objectif professionnel) ===
    ("Développeur passionné avec 5 ans d'expérience dans le développement web. Expertise en React et Node.js.",
     {"cats": {"HEADER": 0.0, "PROFILE": 1.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("PROFIL\nIngénieur Cloud certifié AWS avec expertise en architecture microservices et DevOps.",
     {"cats": {"HEADER": 0.0, "PROFILE": 1.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Objectif: Intégrer une équipe dynamique en tant que Data Scientist pour contribuer à des projets innovants.",
     {"cats": {"HEADER": 0.0, "PROFILE": 1.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("À PROPOS DE MOI\nJeune diplômé motivé, rigoureux et créatif. Passionné par les nouvelles technologies.",
     {"cats": {"HEADER": 0.0, "PROFILE": 1.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("RÉSUMÉ\nConsultant IT avec 8 ans d'expérience en transformation digitale et gestion de projets Agile.",
     {"cats": {"HEADER": 0.0, "PROFILE": 1.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === EDUCATION (formations) ===
    ("FORMATION\n2018-2020: Master Informatique - Université Paris-Saclay\n2015-2018: Licence Informatique - Université de Lyon",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 1.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("FORMATIONS\nDiplôme d'Ingénieur - IMT Nord Europe (2018-2023)\nBaccalauréat S mention Très Bien (2018)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 1.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("ÉDUCATION\nMaster Data Science - École Polytechnique (2019-2021)\nLicence Mathématiques - Sorbonne (2016-2019)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 1.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Formation\nEPITA : Dernière année du cycle ingénieur (Kremlin-Bicêtre)\nLycée Hoche : Baccalauréat S (Versailles)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 1.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("CURSUS SCOLAIRE\nPrépa MPSI/MP* - Lycée Louis-le-Grand (2016-2018)\nBac S mention TB - Lycée Henri IV (2016)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 1.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("PARCOURS ACADÉMIQUE\n2020-2022: Master MIAGE - Paris-Dauphine\n2017-2020: Licence Info - Université de Nantes",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 1.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === EXPERIENCE (expériences professionnelles) ===
    ("EXPÉRIENCE PROFESSIONNELLE\n2021-Présent: Lead DevOps - Amazon Web Services\n2018-2021: Ingénieur DevOps - Capgemini",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 1.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("EXPÉRIENCES\nDéveloppeur Python chez Google (2019-2022)\n- Développement d'APIs REST\n- Mise en place CI/CD",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 1.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("PARCOURS PROFESSIONNEL\nConsultant IT - Sopra Steria (2018-2020)\nStage Développeur - Orange (2017-2018)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 1.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Expériences\nS3 2024-2025 Rhine-Waal University, Allemagne\n- Programme d'échange data science\nS2 2023 Paris\n- Stage chez I NETUM en tant que développeur ABAP",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 1.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("PROFESSIONAL EXPERIENCE\n2022-Present: Software Engineer - Google\n2019-2022: Junior Developer - Microsoft",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 1.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("STAGES ET ALTERNANCES\nAlternance 2 ans - Ingénieur Cloud chez Orange\nStage 6 mois - Développeur chez Thales",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 1.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === SKILLS (compétences) ===
    ("COMPÉTENCES TECHNIQUES\nPython, Java, JavaScript, SQL\nDocker, Kubernetes, AWS, Azure\nGit, GitLab CI, Jenkins",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 1.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("COMPÉTENCES\nLangages: Python, Java, C++\nFrameworks: React, Angular, Django\nBases de données: PostgreSQL, MongoDB",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 1.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Savoirs-faire: Analyse de données, Machine Learning, Deep Learning, NLP, Computer Vision",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 1.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("TECHNICAL SKILLS\nProgramming: Python, Java, JavaScript, TypeScript\nCloud: AWS, GCP, Azure\nDevOps: Docker, K8s, Terraform",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 1.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Compétences fonctionnelles: Gestion de projet, Méthodologie Agile, SCRUM, Communication",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 1.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("OUTILS ET TECHNOLOGIES\nIDE: VS Code, IntelliJ, PyCharm\nVersionning: Git, GitHub, GitLab\nCI/CD: Jenkins, GitHub Actions",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 1.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === LANGUAGES (langues) ===
    ("LANGUES\nFrançais: Natif\nAnglais: Courant (TOEIC 920)\nEspagnol: Intermédiaire (B2)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 1.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Langues parlées: Français (langue maternelle), Anglais (bilingue), Allemand (notions)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 1.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("LANGUAGES\nFrench: Native\nEnglish: Fluent (C1)\nGerman: Basic (A2)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 1.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Français (natif), Anglais (courant - TOEFL 100), Espagnol (intermédiaire B1)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 1.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === PROJECTS (projets) ===
    ("PROJETS PERSONNELS\n• Application mobile de suivi fitness (React Native, Firebase)\n• Bot Discord en Python",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 1.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("PROJETS\nSite e-commerce - Stack MERN\nAPI REST microservices - Spring Boot, Docker",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 1.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("S2 2022 – 2023 Kremlin Bicêtre : Projets\n- Implémentation API avec authentification\n- Système de gestion mémoire en C",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 1.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("RÉALISATIONS\nDashboard analytics - Python, Plotly, Flask\nChatbot IA - OpenAI API, LangChain",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 1.0, "CERTIFICATIONS": 0.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === CERTIFICATIONS ===
    ("CERTIFICATIONS\n• AWS Solutions Architect Professional\n• Certified Kubernetes Administrator (CKA)\n• Google Cloud Professional",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 1.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("Certifications: TOEIC 920, PSM I (Scrum), ITIL v4",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 1.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    ("AWS Cloud Practitioner (2022)\nAzure Fundamentals AZ-900 (2023)\nTerraform Associate (2024)",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 1.0, "INTERESTS": 0.0, "OTHER": 0.0}}),
    
    # === INTERESTS (loisirs/intérêts) ===
    ("CENTRES D'INTÉRÊT\nVoyages, Photographie, VTT, Escalade, Lecture",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 1.0, "OTHER": 0.0}}),
    ("LOISIRS\nSport: Football, Tennis\nMusique: Guitare\nAssociatif: Bénévole Croix-Rouge",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 1.0, "OTHER": 0.0}}),
    ("HOBBIES\nTravels, Photography, Hiking, Reading tech blogs, Open source contributions",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 1.0, "OTHER": 0.0}}),
    ("Intérêts: Hackathons, Meetups tech, Podcasts IA, Veille technologique",
     {"cats": {"HEADER": 0.0, "PROFILE": 0.0, "EDUCATION": 0.0, "EXPERIENCE": 0.0, "SKILLS": 0.0, "LANGUAGES": 0.0, "PROJECTS": 0.0, "CERTIFICATIONS": 0.0, "INTERESTS": 1.0, "OTHER": 0.0}}),
]

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def validate_training_data(data):
    """Valide les données d'entraînement NER."""
    errors = []
    for i, (text, annotations) in enumerate(data):
        entities = annotations.get("entities", [])
        for start, end, label in entities:
            if start < 0 or end > len(text):
                errors.append(f"Exemple {i}: indices hors limites ({start}, {end}) pour texte de longueur {len(text)}")
            elif start >= end:
                errors.append(f"Exemple {i}: start >= end ({start}, {end})")
            else:
                extracted = text[start:end]
                if not extracted.strip():
                    errors.append(f"Exemple {i}: entité vide à ({start}, {end})")
    return errors


def get_ner_labels():
    """Retourne la liste des labels NER utilisés."""
    labels = set()
    for text, annotations in NER_TRAINING_DATA:
        for start, end, label in annotations.get("entities", []):
            labels.add(label)
    return sorted(labels)


def get_textcat_labels():
    """Retourne la liste des catégories de sections."""
    return SECTION_CATEGORIES


if __name__ == "__main__":
    # Validation des données
    print("=== Validation des données NER ===")
    errors = validate_training_data(NER_TRAINING_DATA)
    if errors:
        print(f"❌ {len(errors)} erreurs trouvées:")
        for e in errors[:10]:
            print(f"  - {e}")
    else:
        print(f"✓ {len(NER_TRAINING_DATA)} exemples NER valides")
    
    print(f"\nLabels NER: {get_ner_labels()}")
    print(f"Catégories TextCat: {get_textcat_labels()}")
    print(f"\n{len(TEXTCAT_TRAINING_DATA)} exemples TextCat")

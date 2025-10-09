import React, { useState } from 'react'
import Navbar from '../../components/Navbar'
import SopraLogo from '../../components/SopraLogo'
import { FileText, Download, Eye, Code, User, Briefcase, GraduationCap, Award } from 'lucide-react'
import './Example.css'

const Example = () => {
  const [viewMode, setViewMode] = useState('visual') // 'visual' ou 'json'

  const templateData = {
    "informations_personnelles": {
      "nom": "Martin",
      "prenom": "Jean",
      "email": "jean.martin@email.com",
      "telephone": "+33 6 12 34 56 78",
      "adresse": "123 Rue de la République, 75001 Paris",
      "date_naissance": "15/03/1990",
      "nationalite": "Française"
    },
    "experience_professionnelle": [
      {
        "poste": "Développeur Full-Stack Senior",
        "entreprise": "TechCorp Solutions",
        "periode": "2020 - Présent",
        "description": "Développement d'applications web avec React et Node.js. Gestion d'équipe de 3 développeurs junior.",
        "competences_utilisees": ["React", "Node.js", "MongoDB", "AWS"]
      },
      {
        "poste": "Développeur Frontend",
        "entreprise": "StartupXYZ",
        "periode": "2018 - 2020",
        "description": "Création d'interfaces utilisateur modernes et responsives. Collaboration étroite avec l'équipe UX/UI.",
        "competences_utilisees": ["Vue.js", "CSS3", "JavaScript", "Git"]
      },
      {
        "poste": "Développeur Web Junior",
        "entreprise": "WebAgency Pro",
        "periode": "2016 - 2018",
        "description": "Développement de sites web pour clients variés. Maintenance et optimisation de sites existants.",
        "competences_utilisees": ["HTML5", "CSS3", "PHP", "MySQL"]
      }
    ],
    "formation": [
      {
        "diplome": "Master Informatique",
        "etablissement": "Université Paris-Saclay",
        "periode": "2014 - 2016",
        "mention": "Bien",
        "specialisation": "Développement Web et Mobile"
      },
      {
        "diplome": "Licence Informatique",
        "etablissement": "Université Paris-Saclay",
        "periode": "2011 - 2014",
        "mention": "Assez Bien"
      }
    ],
    "competences": {
      "techniques": {
        "langages": ["JavaScript", "Python", "PHP", "Java"],
        "frameworks": ["React", "Vue.js", "Node.js", "Express"],
        "bases_donnees": ["MongoDB", "MySQL", "PostgreSQL"],
        "outils": ["Git", "Docker", "AWS", "Figma"]
      },
      "soft_skills": ["Leadership", "Travail en équipe", "Communication", "Résolution de problèmes"]
    },
    "langues": [
      {
        "langue": "Français",
        "niveau": "Natif"
      },
      {
        "langue": "Anglais",
        "niveau": "Courant (C1)"
      },
      {
        "langue": "Espagnol",
        "niveau": "Intermédiaire (B2)"
      }
    ],
    "certifications": [
      {
        "nom": "AWS Certified Developer",
        "organisme": "Amazon Web Services",
        "date": "2022"
      },
      {
        "nom": "React Developer Certification",
        "organisme": "Meta",
        "date": "2021"
      }
    ],
    "centres_interet": ["Développement open source", "Photographie", "Randonnée", "Lecture technique"]
  }

  const downloadJSON = () => {
    const dataStr = JSON.stringify(templateData, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = 'template_cv_standardise.json'
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  return (
    <div className="example-page">
      <Navbar />
      
      {/* Hero Section */}
      <section className="example-hero">
        <div className="example-container">
          <div className="text-center">
            <SopraLogo className="hero-logo" />
            <h1 className="hero-title">
              Exemple de CV <span className="gradient-text">standardisé</span>
            </h1>
            <p className="hero-subtitle">
              Découvrez à quoi ressemble un CV après traitement par notre IA
            </p>
            
            <div className="view-toggle">
              <button 
                className={`toggle-btn ${viewMode === 'visual' ? 'active' : ''}`}
                onClick={() => setViewMode('visual')}
              >
                <Eye className="w-4 h-4" />
                Vue visuelle
              </button>
              <button 
                className={`toggle-btn ${viewMode === 'json' ? 'active' : ''}`}
                onClick={() => setViewMode('json')}
              >
                <Code className="w-4 h-4" />
                Format JSON
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="example-content">
        <div className="example-container">
          {viewMode === 'visual' ? (
            <div className="cv-visual">
              <div className="cv-document">
                {/* En-tête */}
                <div className="cv-header">
                  <div className="cv-photo-placeholder">
                    <User className="w-16 h-16 text-gray-400" />
                  </div>
                  <div className="cv-identity">
                    <h2 className="cv-name">
                      {templateData.informations_personnelles.prenom} {templateData.informations_personnelles.nom}
                    </h2>
                    <p className="cv-title">Développeur Full-Stack Senior</p>
                    <div className="cv-contact">
                      <p>{templateData.informations_personnelles.email}</p>
                      <p>{templateData.informations_personnelles.telephone}</p>
                      <p>{templateData.informations_personnelles.adresse}</p>
                    </div>
                  </div>
                </div>

                {/* Expérience */}
                <div className="cv-section">
                  <div className="cv-section-header">
                    <Briefcase className="section-icon" />
                    <h3>Expérience Professionnelle</h3>
                  </div>
                  {templateData.experience_professionnelle.map((exp, index) => (
                    <div key={index} className="cv-item">
                      <div className="cv-item-header">
                        <h4>{exp.poste}</h4>
                        <span className="cv-period">{exp.periode}</span>
                      </div>
                      <p className="cv-company">{exp.entreprise}</p>
                      <p className="cv-description">{exp.description}</p>
                      <div className="cv-skills">
                        {exp.competences_utilisees.map((skill, idx) => (
                          <span key={idx} className="cv-skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Formation */}
                <div className="cv-section">
                  <div className="cv-section-header">
                    <GraduationCap className="section-icon" />
                    <h3>Formation</h3>
                  </div>
                  {templateData.formation.map((form, index) => (
                    <div key={index} className="cv-item">
                      <div className="cv-item-header">
                        <h4>{form.diplome}</h4>
                        <span className="cv-period">{form.periode}</span>
                      </div>
                      <p className="cv-company">{form.etablissement}</p>
                      {form.mention && <p className="cv-mention">Mention : {form.mention}</p>}
                      {form.specialisation && <p className="cv-description">{form.specialisation}</p>}
                    </div>
                  ))}
                </div>

                {/* Compétences */}
                <div className="cv-section">
                  <div className="cv-section-header">
                    <Award className="section-icon" />
                    <h3>Compétences</h3>
                  </div>
                  <div className="cv-skills-grid">
                    <div className="cv-skill-category">
                      <h4>Langages</h4>
                      <div className="cv-skills">
                        {templateData.competences.techniques.langages.map((lang, idx) => (
                          <span key={idx} className="cv-skill-tag">{lang}</span>
                        ))}
                      </div>
                    </div>
                    <div className="cv-skill-category">
                      <h4>Frameworks</h4>
                      <div className="cv-skills">
                        {templateData.competences.techniques.frameworks.map((fw, idx) => (
                          <span key={idx} className="cv-skill-tag">{fw}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Langues */}
                <div className="cv-section">
                  <div className="cv-section-header">
                    <FileText className="section-icon" />
                    <h3>Langues</h3>
                  </div>
                  <div className="cv-languages">
                    {templateData.langues.map((lang, index) => (
                      <div key={index} className="cv-language">
                        <span className="cv-language-name">{lang.langue}</span>
                        <span className="cv-language-level">{lang.niveau}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="json-view">
              <div className="json-header">
                <h3>Format JSON standardisé</h3>
                <button onClick={downloadJSON} className="btn-primary">
                  <Download className="w-4 h-4" />
                  Télécharger JSON
                </button>
              </div>
              <pre className="json-content">
                {JSON.stringify(templateData, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </section>

      {/* Info Section */}
      <section className="info-section">
        <div className="example-container">
          <div className="info-grid">
            <div className="info-card">
              <h3>Structure standardisée</h3>
              <p>Toutes les informations sont organisées selon un format cohérent et professionnel.</p>
            </div>
            <div className="info-card">
              <h3>Données structurées</h3>
              <p>Format JSON facilement exploitable par vos systèmes RH et bases de données.</p>
            </div>
            <div className="info-card">
              <h3>Compatible ATS</h3>
              <p>Format optimisé pour les systèmes de suivi des candidatures (ATS).</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Example
import React from 'react'
import Navbar from '../../components/Navbar'
import SopraLogo from '../../components/SopraLogo'
import { Upload, FileText, Download, CheckCircle, ArrowRight, Zap, Shield, Clock } from 'lucide-react'
import './HowItWorks.css'

const HowItWorks = () => {
  const steps = [
    {
      icon: Upload,
      title: "1. Téléchargez votre CV",
      description: "Sélectionnez votre CV au format .docx depuis votre ordinateur. Notre système accepte tous les formats de CV, même les plus désorganisés.",
      details: ["Formats acceptés : .docx", "Taille max : 10MB", "Toutes mises en forme acceptées"]
    },
    {
      icon: FileText,
      title: "2. Analyse automatique",
      description: "Notre intelligence artificielle analyse et extrait automatiquement toutes les informations importantes de votre CV.",
      details: ["Extraction des données personnelles", "Identification des compétences", "Analyse de l'expérience professionnelle", "Reconnaissance de la formation"]
    },
    {
      icon: CheckCircle,
      title: "3. Standardisation",
      description: "Les informations sont organisées selon un format professionnel standardisé, prêt pour les RH.",
      details: ["Format uniforme", "Structure professionnelle", "Mise en page optimisée", "Compatible ATS"]
    },
    {
      icon: Download,
      title: "4. Téléchargement",
      description: "Récupérez votre CV standardisé au format JSON ou générez un nouveau document Word formaté.",
      details: ["Export JSON", "Export Word", "Données structurées", "Prêt à l'emploi"]
    }
  ]

  const features = [
    {
      icon: Zap,
      title: "Traitement rapide",
      description: "Analysez votre CV en moins de 2 minutes grâce à notre IA avancée."
    },
    {
      icon: Shield,
      title: "Sécurisé",
      description: "Vos données sont traitées en toute sécurité et ne sont jamais stockées."
    },
    {
      icon: Clock,
      title: "Disponible 24/7",
      description: "Utilisez notre service à tout moment, où que vous soyez."
    }
  ]

  return (
    <div className="how-it-works-page">
      <Navbar />
      
      {/* Hero Section */}
      <section className="how-it-works-hero">
        <div className="how-it-works-container">
          <div className="text-center">
            <SopraLogo className="hero-logo" />
            <h1 className="hero-title">
              Comment ça <span className="gradient-text">fonctionne</span> ?
            </h1>
            <p className="hero-subtitle">
              Découvrez comment notre outil transforme vos CV désorganisés en documents professionnels standardisés
            </p>
          </div>
        </div>
      </section>

      {/* Étapes détaillées */}
      <section className="steps-section">
        <div className="how-it-works-container">
          <div className="text-center mb-16">
            <h2 className="section-title">
              Comment <span className="gradient-text">l'utiliser</span>
            </h2>
            <p className="section-subtitle">
              4 étapes simples pour transformer votre CV
            </p>
          </div>

          <div className="steps-grid">
            {steps.map((step, index) => (
              <div key={index} className="step-card">
                <div className="step-icon-wrapper">
                  <step.icon className="step-icon" />
                </div>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-description">{step.description}</p>
                <ul className="step-details">
                  {step.details.map((detail, idx) => (
                    <li key={idx}>{detail}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Fonctionnalités */}
      <section className="features-section">
        <div className="how-it-works-container">
          <div className="text-center mb-16">
            <h2 className="section-title">
              Pourquoi choisir notre <span className="gradient-text">solution</span>
            </h2>
          </div>

          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon-wrapper">
                  <feature.icon className="feature-icon" />
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="how-it-works-container">
          <div className="cta-content">
            <h2 className="cta-title">Prêt à standardiser vos CV ?</h2>
            <p className="cta-subtitle">
              Commencez dès maintenant et transformez vos CV en documents professionnels
            </p>
            <div className="cta-buttons">
              <a href="/start" className="btn-primary">
                Commencer maintenant
                <ArrowRight className="w-5 h-5" />
              </a>
              <a href="/example" className="btn-secondary">
                Voir un exemple
                <FileText className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HowItWorks
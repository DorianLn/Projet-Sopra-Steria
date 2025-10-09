import React, { useState } from 'react'
import Navbar from '../../components/Navbar'
import SopraLogo from '../../components/SopraLogo'
import { Upload, FileText, ArrowRight } from 'lucide-react'
import './Start.css'

const Start = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file && file.name.endsWith('.docx')) {
      setSelectedFile(file)
    } else {
      alert('Veuillez sélectionner un fichier .docx')
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith('.docx')) {
      setSelectedFile(file)
    } else {
      alert('Veuillez sélectionner un fichier .docx')
    }
  }

  const handleSubmit = () => {
    if (selectedFile) {
      // Ici vous pourrez traiter le fichier avec votre backend
      console.log('Fichier à traiter:', selectedFile.name)
      alert(`Traitement du fichier: ${selectedFile.name}`)
    }
  }

  return (
    <div className="start-page">
      <Navbar />
      <main className="start-section">
        <div className="start-container">
          <div className="text-center max-w-4xl mx-auto">
            <SopraLogo className="hero-logo" />
            <h1 className="hero-title">
              Commencez l'extraction de votre <span className="gradient-text">CV</span>
            </h1>
            <p className="hero-subtitle">
              Téléchargez votre CV au format .docx et obtenez un document standardisé en quelques secondes.
            </p>
            
            {/* Zone de téléchargement de fichier */}
            <div className="mt-12">
              <div 
                className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input 
                  type="file" 
                  accept=".docx"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                  id="cv-upload"
                />
                
                <div className="upload-content">
                  <Upload className="upload-icon" />
                  
                  {selectedFile ? (
                    <div className="space-y-4">
                      <div className="file-selected">
                        <FileText className="file-selected-icon" />
                        <span className="file-selected-name">{selectedFile.name}</span>
                      </div>
                      <p className="file-ready">
                        Fichier prêt à être traité
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <h3 className="upload-title">
                        Glissez-déposez votre CV ici
                      </h3>
                      <p className="upload-description">
                        ou cliquez pour sélectionner un fichier
                      </p>
                      <p className="upload-format">
                        Formats acceptés : .docx uniquement
                      </p>
                    </div>
                  )}
                </div>
              </div>
              
              {selectedFile && (
                <div className="submit-section">
                  <button 
                    onClick={handleSubmit}
                    className="submit-button"
                  >
                    Traiter le CV
                    <ArrowRight />
                  </button>
                </div>
              )}
            </div>

            {/* Informations supplémentaires */}
            <div className="process-steps">
              <div className="process-step">
                <div className="step-icon">
                  <Upload />
                </div>
                <h3 className="step-title">1. Téléchargez</h3>
                <p className="step-description">
                  Sélectionnez votre CV au format .docx
                </p>
              </div>
              
              <div className="process-step">
                <div className="step-icon">
                  <FileText />
                </div>
                <h3 className="step-title">2. Traitement</h3>
                <p className="step-description">
                  Nous allons extraire automatiquement les informations
                </p>
              </div>
              
              <div className="process-step">
                <div className="step-icon">
                  <ArrowRight />
                </div>
                <h3 className="step-title">3. Résultat</h3>
                <p className="step-description">
                  Recevez votre document standardisé
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Start
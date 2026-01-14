import React, { useState } from 'react';
import Navbar from '../../components/Navbar';
import SopraLogo from '../../components/SopraLogo';
import {
  Upload,
  FileText,
  ArrowRight,
  Download,
  CheckCircle,
  AlertCircle,
  File
} from 'lucide-react';
import './Normalize.css';

const Normalize = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [consentChecked, setConsentChecked] = useState(false);

  // --- Gestion du drag & drop ---
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect({ target: { files: [file] } });
  };

  // --- Sélection du fichier ---
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && (file.name.endsWith('.json') || file.name.endsWith('.docx'))) {
      setSelectedFile(file);
      setError(null);
      setResult(null);
      setMetadata(null);
    } else {
      alert('Veuillez sélectionner un fichier .json ou .docx');
    }
  };

  // --- Soumission vers le backend ---
  const handleSubmit = async () => {
    if (!selectedFile) return alert('Veuillez sélectionner un fichier');

    const formData = new FormData();
    formData.append('file', selectedFile);

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/cv/normalize', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Erreur lors de la normalisation');

      setResult(data.cv_normalized);
      setMetadata(data.metadata);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --- Télécharger le JSON normalisé ---
  const downloadJson = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cv_normalized_v2.0.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  // --- Télécharger en DOCX ---
  const downloadDocx = async () => {
    if (!result) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/cv/normalize/docx', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cv_data: result })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erreur lors de la génération du DOCX');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cv_normalized.docx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Erreur : ' + error.message);
    }
  };

  // --- Télécharger en PDF ---
  const downloadPdf = async () => {
    if (!result) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/cv/normalize/pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cv_data: result })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erreur lors de la génération du PDF');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cv_normalized.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Erreur : ' + error.message);
    }
  };

  return (
    <div className="normalize-page">
      <Navbar />
      <main className="normalize-section">
        <div className="normalize-container text-center max-w-5xl mx-auto">
          <SopraLogo className="hero-logo" />
          <h1 className="hero-title">
            Normaliser votre <span className="gradient-text">CV</span>
          </h1>
          <p className="hero-subtitle">
            Convertissez un ancien CV au nouveau format v2.0 pour une meilleure compatibilité.
          </p>

          {/* Zone de téléchargement */}
          <div className="mt-10 relative">
            <div
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".json,.docx"
                onChange={handleFileSelect}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="upload-content">
                <Upload className="upload-icon" />
                {selectedFile ? (
                  <div className="space-y-2">
                    <div className="file-selected">
                      <FileText className="file-selected-icon" />
                      <span className="file-selected-name">{selectedFile.name}</span>
                    </div>
                    <p className="file-ready">Fichier prêt à être normalisé</p>
                  </div>
                ) : (
                  <>
                    <h3 className="upload-title">Glissez-déposez votre ancien CV ici</h3>
                    <p className="upload-description">ou cliquez pour sélectionner un fichier</p>
                    <p className="upload-format">Formats acceptés : .json, .docx</p>
                  </>
                )}
              </div>
            </div>

            {/* Bouton de traitement */}
            {selectedFile && (
              <div className="submit-section">
                <div className="consent-container">
                  <label className="consent-label">
                    <input
                      type="checkbox"
                      checked={consentChecked}
                      onChange={(e) => setConsentChecked(e.target.checked)}
                      className="consent-checkbox"
                    />
                    <span className="consent-text">
                      J'autorise le traitement de mon CV à des fins d'analyse et de génération de documents. 
                      Je comprends que mes données personnelles seront traitées de manière confidentielle 
                      et ne seront pas partagées avec des tiers. Ce traitement est effectué localement 
                      et aucune donnée n'est transmise à des serveurs externes.
                    </span>
                  </label>
                </div>
                <button
                  onClick={handleSubmit}
                  disabled={loading || !consentChecked}
                  className="submit-button"
                >
                  {loading ? 'Normalisation en cours...' : 'Normaliser le CV'}
                  <ArrowRight />
                </button>
              </div>
            )}
          </div>

          {/* Gestion des erreurs */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md flex items-start gap-3">
              <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={18} />
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Résultat affiché */}
          {result && (
            <div className="result-section text-left mt-10">
              {/* Barre de succès */}
              <div className="success-banner">
                <CheckCircle className="success-icon" />
                <div>
                  <h3>Normalisation réussie !</h3>
                  <p>Votre CV a été converti au format v2.0</p>
                </div>
              </div>

              {/* Métadonnées */}
              {metadata && (
                <div className="metadata-grid mt-6">
                  <div className="metadata-card">
                    <span className="metadata-label">Version</span>
                    <span className="metadata-value">{metadata.version_cible}</span>
                  </div>
                  <div className="metadata-card">
                    <span className="metadata-label">Expériences</span>
                    <span className="metadata-value">{metadata.nb_experiences}</span>
                  </div>
                  <div className="metadata-card">
                    <span className="metadata-label">Formations</span>
                    <span className="metadata-value">{metadata.nb_formations}</span>
                  </div>
                  <div className="metadata-card">
                    <span className="metadata-label">Compétences</span>
                    <span className="metadata-value">{metadata.nb_competences}</span>
                  </div>
                  <div className="metadata-card">
                    <span className="metadata-label">Langues</span>
                    <span className="metadata-value">{metadata.nb_langues}</span>
                  </div>
                </div>
              )}

              {/* Boutons d'export */}
              <div className="export-section mt-8">
                <button onClick={downloadJson} className="export-button">
                  <Download size={18} />
                  Télécharger JSON v2.0
                </button>
                <button onClick={downloadDocx} className="export-button export-button-docx">
                  <FileText size={18} />
                  Télécharger DOCX
                </button>
                <button onClick={downloadPdf} className="export-button export-button-pdf">
                  <File size={18} />
                  Télécharger PDF
                </button>
              </div>

              {/* Aperçu du JSON */}
              <div className="json-preview mt-8">
                <h3 className="preview-title">Aperçu du CV normalisé</h3>
                <div className="json-container">
                  <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Normalize;

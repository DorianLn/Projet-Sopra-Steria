import React, { useState } from 'react';
import Navbar from '../../components/Navbar';
import SopraLogo from '../../components/SopraLogo';
import { Upload, FileText, ArrowRight } from 'lucide-react';
import './Start.css';

const Start = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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
    if (file && (file.name.endsWith('.docx') || file.name.endsWith('.pdf'))) {
      setSelectedFile(file);
      setError(null);
      setResult(null);
    } else {
      alert('Veuillez sélectionner un fichier .docx ou .pdf');
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
      const response = await fetch('http://localhost:5000/api/cv/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Erreur lors de l’analyse');

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="start-page">
      <Navbar />
      <main className="start-section">
        <div className="start-container text-center max-w-5xl mx-auto">
          <SopraLogo className="hero-logo" />
          <h1 className="hero-title">
            Analysez votre <span className="gradient-text">CV</span>
          </h1>
          <p className="hero-subtitle">
            Téléversez votre CV (.docx ou .pdf) pour une extraction automatique des informations clés.
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
                accept=".docx,.pdf"
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
                    <p className="file-ready">Fichier prêt à être analysé</p>
                  </div>
                ) : (
                  <>
                    <h3 className="upload-title">Glissez-déposez votre CV ici</h3>
                    <p className="upload-description">ou cliquez pour sélectionner un fichier</p>
                    <p className="upload-format">Formats acceptés : .docx, .pdf</p>
                  </>
                )}
              </div>
            </div>

            {/* Bouton de traitement */}
            {selectedFile && (
              <div className="submit-section">
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="submit-button"
                >
                  {loading ? 'Analyse en cours...' : 'Analyser le CV'}
                  <ArrowRight />
                </button>
              </div>
            )}
          </div>

          {/* Gestion des erreurs */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
              {error}
            </div>
          )}

          {/* Résultat affiché */}
          {result && (
            <div className="result-section text-left mt-10 p-6 bg-white shadow-lg rounded-xl space-y-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Résultats de l’analyse</h2>

              {/* Contact */}
              {result.contact && (
                <div>
                  <h3 className="font-semibold text-gray-700">📞 Contact</h3>
                  <ul className="list-disc list-inside text-gray-600">
                    {result.contact.nom && <li>Nom : {result.contact.nom}</li>}
                    {result.contact.email && <li>Email : {result.contact.email}</li>}
                    {result.contact.telephone && <li>Téléphone : {result.contact.telephone}</li>}
                    {result.contact.adresse && <li>Adresse : {result.contact.adresse}</li>}
                  </ul>
                </div>
              )}

              {/* Formations */}
              {result.formations?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700">🎓 Formations</h3>
                  <ul className="list-disc list-inside text-gray-600">
                    {result.formations.map((f, i) => (
                      <li key={i}>{f.etablissement} - {f.dates}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Expériences */}
              {result.experiences?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700">💼 Expériences</h3>
                  <ul className="list-disc list-inside text-gray-600">
                    {result.experiences.map((exp, i) => (
                      <li key={i}>{exp.entreprise} - {exp.dates}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Compétences */}
              {result.competences?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700">🧠 Compétences</h3>
                  <ul className="list-disc list-inside text-gray-600">
                    {result.competences.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}

              {/* Langues */}
              {result.langues?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700">🌍 Langues</h3>
                  <ul className="list-disc list-inside text-gray-600">
                    {result.langues.map((l, i) => <li key={i}>{l}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Étapes visuelles */}
          <div className="process-steps mt-16">
            <div className="process-step">
              <div className="step-icon"><Upload /></div>
              <h3 className="step-title">1. Téléversez</h3>
              <p className="step-description">Choisissez votre CV .docx ou .pdf</p>
            </div>

            <div className="process-step">
              <div className="step-icon"><FileText /></div>
              <h3 className="step-title">2. Analyse</h3>
              <p className="step-description">Extraction automatique des données</p>
            </div>

            <div className="process-step">
              <div className="step-icon"><ArrowRight /></div>
              <h3 className="step-title">3. Résultat</h3>
              <p className="step-description">Affichage structuré et clair</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Start;

import React, { useState } from 'react';
import Navbar from '../../components/Navbar';
import SopraLogo from '../../components/SopraLogo';
import {
  Upload,
  FileText,
  ArrowRight,
  Download,
  BarChart3,
  FileDown,
  Eye
} from 'lucide-react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import './Start.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

// ---- Helpers ----
const computeExtractionScore = (result) => {
  if (!result) return 0;
  let score = 0;

  const weights = {
    contact: 25,
    formations: 15,
    experiences: 20,
    competences: 20,
    langues: 10,
    projets: 5,
    certifications: 3,
    disponibilite: 2
  };

  if (result.contact?.nom && result.contact?.email) score += weights.contact;
  if (result.formations?.length) score += weights.formations;
  if (result.experiences?.length) score += weights.experiences;
  if (
    result.competences &&
    (result.competences.techniques ||
      result.competences.fonctionnelles)
  ) {
    score += weights.competences;
  }
  if (result.langues?.length) score += weights.langues;
  if (result.projets?.length) score += weights.projets;
  if (result.certifications?.length) score += weights.certifications;
  if (result.disponibilite) score += weights.disponibilite;

  // --- Penalties ---
  let penalties = 0;

  // Nom mal extrait (contient un métier ou trop de mots)
  if (result.contact?.nom && /développeur|ingénieur|chef|manager/i.test(result.contact.nom)) {
    penalties += 10;
  }

  // Dates incohérentes
  result.experiences?.forEach((exp) => {
    const years = exp.dates?.match(/(19|20)\d{2}/g);
    if (years && years.length === 2) {
      if (parseInt(years[1]) < parseInt(years[0])) penalties += 8;
    }
  });

  // Exp sans dates
  const emptyDatesCount = result.experiences?.filter(e => !e.dates)?.length || 0;
  penalties += emptyDatesCount * 5;

  // Doublons entreprises
  const entreprises = new Set();
  result.experiences?.forEach(e => {
    if (entreprises.has(e.entreprise)) penalties += 5;
    entreprises.add(e.entreprise);
  });

  score -= penalties;

  return Math.max(0, Math.min(100, score));
};

const computeProfessionalCvScore = (result) => {
  if (!result) return 0;
  let score = 0;

  // 1) Richesse compétences
  let comp = [];

  if (result.competences) {
    if (result.competences.techniques) {
      comp = Object.values(result.competences.techniques).flat();
    }
  
    if (result.competences.fonctionnelles) {
      comp = comp.concat(result.competences.fonctionnelles);
    }
  }
  
  const hasBackend = comp.some(c => /python|java|spring|node|django|c\+\+/i.test(c));
  const hasFrontend = comp.some(c => /react|angular|vue|html|css|javascript/i.test(c));
  const hasCloud = comp.some(c => /aws|azure|gcp|cloud|docker|kubernetes|ci\/cd/i.test(c));
  const hasSoft = comp.some(c => /communication|leadership|gestion/i.test(c));

  score += (hasBackend + hasFrontend + hasCloud + hasSoft) * 5; // max 20

  // 2) Expérience totale
  const years = estimateExperienceLevel(result).years;
  if (years >= 7) score += 20;
  else if (years >= 4) score += 15;
  else if (years >= 2) score += 10;
  else if (years >= 1) score += 5;

  // 3) Études
  const formations = result.formations || [];
  if (formations.some(f => /master|bac\+5|ingénieur/i.test(f.etablissement))) score += 15;
  else if (formations.some(f => /licence|bac\+3/i.test(f.etablissement))) score += 10;
  else if (formations.length) score += 5;

  // 4) Projets / réalisations
  if (result.projets?.length >= 3) score += 10;
  else if (result.projets?.length === 2) score += 7;
  else if (result.projets?.length === 1) score += 4;

  // 5) Langues
  if (result.langues?.length >= 2) score += 10;
  else if (result.langues?.length === 1) score += 5;

  // 6) Cohérence globale
  let coherence = 15;

  // incohérence simple : dates inversées
  result.experiences?.forEach((exp) => {
    const years = exp.dates?.match(/(19|20)\d{2}/g);
    if (years && years.length === 2 && parseInt(years[1]) < parseInt(years[0])) {
      coherence -= 5;
    }
  });

  score += Math.max(0, coherence);

  // 7) Structure claire
  const structureSections =
    (result.contact ? 1 : 0) +
    (result.formations?.length ? 1 : 0) +
    (result.experiences?.length ? 1 : 0) +
    (result.competences &&
      (result.competences.techniques ||
       result.competences.fonctionnelles) ? 1 : 0);
  score += structureSections * 3; // max 12

  return Math.min(100, score);
};


const estimateExperienceLevel = (result) => {
  if (!result?.experiences?.length) return { label: 'Non déterminé', years: 0 };

  let minYear = 9999;
  let maxYear = 0;

  const extractYear = (str) => {
    if (!str) return null;
    const range = str.match(/(19|20)\d{2}.*(19|20)\d{2}/);
    if (range) {
      const years = str.match(/(19|20)\d{2}/g);
      if (years && years.length >= 2) {
        return { start: parseInt(years[0], 10), end: parseInt(years[1], 10) };
      }
    }
    const single = str.match(/(19|20)\d{2}/);
    if (single) {
      const y = parseInt(single[0], 10);
      return { start: y, end: y };
    }
    return null;
  };

  result.experiences.forEach((exp) => {
    const parsed = extractYear(exp.dates);
    if (parsed) {
      minYear = Math.min(minYear, parsed.start);
      maxYear = Math.max(maxYear, parsed.end);
    }
  });

  if (minYear === 9999 || maxYear === 0) return { label: 'Non déterminé', years: 0 };
  const years = Math.max(0, maxYear - minYear + 1);

  let label = 'Junior';
  if (years >= 5) label = 'Senior';
  else if (years >= 2) label = 'Intermédiaire';

  return { label, years };
};

const buildRadarData = (result) => {
  if (!result || !result.competences) {
    return {
      labels: ['Compétences'],
      datasets: [
        {
          label: 'Compétences',
          data: [1]
        }
      ]
    };
  }

  let competences = [];

  if (result.competences.techniques) {
    competences = Object.values(result.competences.techniques).flat();
  }

  competences = competences.slice(0, 7);

  if (!competences.length) {
    return {
      labels: ['Compétences'],
      datasets: [
        {
          label: 'Compétences',
          data: [1]
        }
      ]
    };
  }

  const values = competences.map(() => 3);

  return {
    labels: competences,
    datasets: [
      {
        label: 'Compétences clés',
        data: values,
        backgroundColor: 'rgba(255, 88, 120, 0.2)',
        borderColor: 'rgba(214, 46, 92, 0.9)',
        borderWidth: 2,
        pointRadius: 3
      }
    ]
  };
};


const downloadJson = (result) => {
  const blob = new Blob([JSON.stringify(result, null, 2)], {
    type: 'application/json'
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cv_analyse.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
};

const exportPdf = () => {
  // version simple : impression de la page (l’utilisateur peut choisir "Enregistrer en PDF")
  window.print();
};

const Start = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [modifiedDocx, setModifiedDocx] = useState(null);

// --- Conversion DOCX modifié en PDF ---
  const convertDocxToPdf = async () => {
    if (!modifiedDocx) {
      alert("Veuillez sélectionner un fichier .docx modifié.");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", modifiedDocx);
  
    try {
      const response = await fetch("http://localhost:5000/api/cv/convert", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "Erreur lors de la conversion");
      }
  
      // Récupérer le PDF retourné
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
  
      const a = document.createElement("a");
      a.href = url;
      a.download = "CV_Final.pdf";
      a.click();
  
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Erreur : " + e.message);
    }
  };
  

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
        body: formData
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

  const extractionScore = computeExtractionScore(result);
  const professionalScore = computeProfessionalCvScore(result);
  const xpInfo = estimateExperienceLevel(result);
  const radarData = buildRadarData(result);

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
            Téléversez votre CV (.docx ou .pdf) pour une extraction automatique
            des informations clés.
          </p>

          {/* Zone de téléchargement */}
          <div className="mt-10 relative">
            <div
              className={`upload-zone ${dragActive ? "drag-active" : ""}`}
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
                      <span className="file-selected-name">
                        {selectedFile.name}
                      </span>
                    </div>
                    <p className="file-ready">Fichier prêt à être analysé</p>
                  </div>
                ) : (
                  <>
                    <h3 className="upload-title">
                      Glissez-déposez votre CV ici
                    </h3>
                    <p className="upload-description">
                      ou cliquez pour sélectionner un fichier
                    </p>
                    <p className="upload-format">
                      Formats acceptés : .docx, .pdf
                    </p>
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
                  {loading ? "Analyse en cours..." : "Analyser le CV"}
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
            <div className="result-section text-left mt-10">
              {/* Barre d’outils / résumé */}
              <div className="result-toolbar">
                {/* Score extraction */}
                <div className="score-block">
                  <span className="score-label">Fiabilité extraction</span>
                  <div className="score-value">
                    <BarChart3 size={18} />
                    <span>{extractionScore}%</span>
                  </div>
                  <div className="score-bar">
                    <div
                      className="score-bar-fill"
                      style={{ width: `${extractionScore}%` }}
                    />
                  </div>

                  {/* Score Pro */}
                  <div className="score-block">
                    <span className="score-label">Score CV Pro</span>
                    <div className="score-value">
                      <BarChart3 size={18} />
                      <span>{professionalScore}%</span>
                    </div>
                    <div className="score-bar">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${professionalScore}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* XP */}
                <div className="xp-block">
                  <span className="xp-label">Niveau d’expérience</span>
                  <span className="xp-pill">
                    {xpInfo.label}{" "}
                    {xpInfo.years > 0 && `(${xpInfo.years} ans estimés)`}
                  </span>
                </div>

                <div className="export-buttons">
                  <button
                    className="export-btn"
                    onClick={() => {
                      const baseName = result.json_filename.replace(
                        ".json",
                        ""
                      );
                      window.open(
                        `http://localhost:5000/api/cv/json/${encodeURIComponent(
                          baseName
                        )}`,
                        "_blank"
                      );
                    }}
                  >
                    <Download size={16} />
                    JSON
                  </button>
                  <button
                    className="export-btn"
                    onClick={() => {
                      if (!result?.pdf_filename) {
                        alert("Aucun PDF généré par le backend.");
                        return;
                      }
                      window.open(
                        `http://localhost:5000/api/cv/pdf/${result.pdf_filename}`,
                        "_blank"
                      );
                    }}
                  >
                    <FileDown size={16} />
                    PDF
                  </button>

                  <button
                    className="export-btn"
                    onClick={() => {
                      if (!result?.json_filename) {
                        alert("Aucun JSON trouvé pour générer le Word.");
                        return;
                      }

                      const baseName = result.json_filename.replace(
                        ".json",
                        ""
                      );

                      window.open(
                        `http://localhost:5000/api/cv/docx/${baseName}`,
                        "_blank"
                      );
                    }}
                  >
                    <FileText size={16} />
                    DOCX
                  </button>
                  {/* Sélection du CV Word modifié */}
                  <input
                    type="file"
                    accept=".docx"
                    style={{ display: "none" }}
                    id="upload-modified-docx"
                    onChange={(e) => setModifiedDocx(e.target.files[0])}
                  />

                  <label htmlFor="upload-modified-docx" className="export-btn">
                    <Upload size={16} />
                    Importer DOCX modifié
                  </label>

                  {/* Convertir en PDF */}
                  <button
                    className="export-btn"
                    onClick={convertDocxToPdf}
                    disabled={!modifiedDocx}
                  >
                    <FileDown size={16} />
                    Convertir en PDF
                  </button>
                </div>
              </div>

              {/* Grille principale */}
              <div className="result-wrapper">
                {/* CONTACT */}
                <div className="result-card">
                  <h3 className="result-title">📞 Contact</h3>
                  <ul className="result-list text-gray-700">
                    {result.contact.nom && (
                      <li>
                        <strong>Nom :</strong> {result.contact.nom}
                      </li>
                    )}
                    {result.contact.email && (
                      <li>
                        <strong>Email :</strong> {result.contact.email}
                      </li>
                    )}
                    {result.contact.telephone && (
                      <li>
                        <strong>Téléphone :</strong> {result.contact.telephone}
                      </li>
                    )}
                    {result.contact.adresse && (
                      <li>
                        <strong>Adresse :</strong> {result.contact.adresse}
                      </li>
                    )}
                  </ul>
                </div>

                {/* FORMATIONS */}
                {result.formations?.length > 0 && (
                  <div className="result-card">
                    <h3 className="result-title">🎓 Formations</h3>
                    <ul className="result-list text-gray-700">
                      {result.formations.map((f, i) => (
                        <li key={i}>
                          <strong>{f.etablissement}</strong> — {f.dates}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* EXPERIENCES */}
                {result.experiences?.length > 0 && (
                  <div className="result-card">
                    <h3 className="result-title">💼 Expériences</h3>
                    <ul className="result-list text-gray-700">
                      {result.experiences.map((e, i) => (
                        <li key={i}>
                          <strong>{e.entreprise}</strong> — {e.poste || "—"} (
                          {e.dates})
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* PROJETS */}
                {result.projets?.length > 0 && (
                  <div className="result-card">
                    <h3 className="result-title">🚀 Projets</h3>
                    <ul className="result-list text-gray-700">
                      {result.projets.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* COMPETENCES (tags + radar) */}
                {result.competences && (
                  <div className="result-card">
                    <h3 className="result-title">🧠 Compétences</h3>

                    {/* COMPÉTENCES TECHNIQUES */}
                    {result.competences.techniques && (
                      <div className="skills-section">
                        <h4 className="skills-section-title">
                          Compétences Techniques
                        </h4>

                        {Object.entries(result.competences.techniques).map(
                          ([categorie, liste]) => (
                            <div key={categorie} className="skills-category">
                              <h5 className="skills-category-title">
                                {categorie}
                              </h5>

                              <div className="skills-tags">
                                {liste.map((c, i) => (
                                  <span key={i} className="skill-tag">
                                    {c}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    )}

                    {/* COMPÉTENCES FONCTIONNELLES */}
                    {result.competences.fonctionnelles &&
                      result.competences.fonctionnelles.length > 0 && (
                        <div className="skills-section">
                          <h4 className="skills-section-title">
                            Compétences Fonctionnelles
                          </h4>

                          <div className="skills-tags">
                            {result.competences.fonctionnelles.map((c, i) => (
                              <span
                                key={i}
                                className="skill-tag skill-functional"
                              >
                                {c}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                  </div>
                )}

                {/* RADAR COMPETENCES */}
                {result.competences?.techniques && Object.values(result.competences.techniques).flat().length > 0 && (
                  <div className="result-card radar-card">
                    <h3 className="result-title">
                      <BarChart3 size={18} /> Radar des compétences
                    </h3>
                    <Radar
                      data={radarData}
                      options={{
                        responsive: true,
                        scales: {
                          r: {
                            suggestedMin: 0,
                            suggestedMax: 5,
                            ticks: { stepSize: 1 },
                          },
                        },
                        plugins: {
                          legend: { display: false },
                        },
                      }}
                    />
                  </div>
                )}

                {/* LANGUES */}
                {result.langues?.length > 0 && (
                  <div className="result-card">
                    <h3 className="result-title">🌍 Langues</h3>
                    <ul className="result-list text-gray-700">
                      {result.langues.map((l, i) => (
                        <li key={i}>{l}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* CERTIFICATIONS */}
                {result.certifications?.length > 0 && (
                  <div className="result-card">
                    <h3 className="result-title">🏅 Certifications</h3>
                    <ul className="result-list text-gray-700">
                      {result.certifications.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* LOISIRS */}
                {result.loisirs?.length > 0 && (
                  <div className="result-card">
                    <h3 className="result-title">🎯 Loisirs</h3>
                    <ul className="result-list text-gray-700">
                      {result.loisirs.map((l, i) => (
                        <li key={i}>{l}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* DISPONIBILITE */}
                {result.disponibilite && (
                  <div className="result-card">
                    <h3 className="result-title">📅 Disponibilité</h3>
                    <p className="text-gray-700">{result.disponibilite}</p>
                  </div>
                )}

                {/* DATES BRUTES */}
                {result.dates?.length > 0 && (
                  <div className="result-card">
                    <h3 className="result-title">🗂 Dates détectées</h3>
                    <ul className="result-list text-gray-700">
                      {result.dates.map((d, i) => (
                        <li key={i}>{d}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* CV RECONSTITUÉ */}
                <div className="result-card cv-preview-card">
                  <h3 className="result-title">
                    <Eye size={18} /> CV reconstitué (vue synthèse)
                  </h3>
                  <div className="cv-preview-body">
                    <h4>{result.contact.nom}</h4>
                    <p className="cv-preview-contact">
                      {result.contact.email} ··· {result.contact.telephone} ···{" "}
                      {result.contact.adresse}
                    </p>

                    {result.formations?.length > 0 && (
                      <>
                        <h5>Formations</h5>
                        <ul>
                          {result.formations.map((f, i) => (
                            <li key={i}>
                              <strong>{f.etablissement}</strong> — {f.dates}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}

                    {result.experiences?.length > 0 && (
                      <>
                        <h5>Expériences</h5>
                        <ul>
                          {result.experiences.map((e, i) => (
                            <li key={i}>
                              <strong>{e.entreprise}</strong> — {e.poste || "—"}{" "}
                              ({e.dates})
                            </li>
                          ))}
                        </ul>
                      </>
                    )}

                    {result.projets?.length > 0 && (
                      <>
                        <h5>Projets</h5>
                        <ul>
                          {result.projets.map((p, i) => (
                            <li key={i}>{p}</li>
                          ))}
                        </ul>
                      </>
                    )}

                    {result.competences && (
                      <>
                        <h5>Compétences clés</h5>

                        {result.competences.techniques && (
                          <p>
                            {Object.values(result.competences.techniques)
                              .flat()
                              .join(" · ")}
                          </p>
                        )}

                        {result.competences.fonctionnelles?.length > 0 && (
                          <p>{result.competences.fonctionnelles.join(" · ")}</p>
                        )}
                      </>
                    )}

                    {result.langues?.length > 0 && (
                      <>
                        <h5>Langues</h5>
                        <p>{result.langues.join(" · ")}</p>
                      </>
                    )}

                    {result.disponibilite && (
                      <>
                        <h5>Disponibilité</h5>
                        <p>{result.disponibilite}</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Étapes visuelles */}
          <div className="process-steps mt-16">
            <div className="process-step">
              <div className="step-icon">
                <Upload />
              </div>
              <h3 className="step-title">1. Téléversez</h3>
              <p className="step-description">
                Choisissez votre CV .docx ou .pdf
              </p>
            </div>

            <div className="process-step">
              <div className="step-icon">
                <FileText />
              </div>
              <h3 className="step-title">2. Analyse</h3>
              <p className="step-description">
                Extraction automatique des données
              </p>
            </div>

            <div className="process-step">
              <div className="step-icon">
                <ArrowRight />
              </div>
              <h3 className="step-title">3. Résultat</h3>
              <p className="step-description">Dashboard d’analyse structuré</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Start;

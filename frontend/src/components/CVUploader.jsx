import React, { useState } from 'react';

const CVUploader = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        setError(null);
        setResult(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError("Veuillez sélectionner un fichier");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:5000/api/cv/analyze', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Une erreur est survenue');
            }

            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6 text-gray-800">Analyser un CV</h2>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">
                            Sélectionner un fichier (PDF ou DOCX)
                        </label>
                        <input
                            type="file"
                            accept=".pdf,.docx"
                            onChange={handleFileChange}
                            className="w-full p-2 border rounded-md"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || !file}
                        className={`w-full py-2 px-4 rounded-md text-white font-medium
                            ${loading || !file 
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700'
                            }`}
                    >
                        {loading ? 'Analyse en cours...' : 'Analyser le CV'}
                    </button>
                </form>

                {error && (
                    <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-red-600">{error}</p>
                    </div>
                )}

                {result && (
                    <div className="mt-6 space-y-4">
                        <h3 className="text-xl font-semibold text-gray-800">Résultats de l'analyse</h3>
                        
                        {/* Contact */}
                        {result.contact && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Contact :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.contact.nom && <li>Nom : {result.contact.nom}</li>}
                                    {result.contact.email && <li>Email : {result.contact.email}</li>}
                                    {result.contact.telephone && <li>Téléphone : {result.contact.telephone}</li>}
                                    {result.contact.adresse && <li>Adresse : {result.contact.adresse}</li>}
                                </ul>
                            </div>
                        )}

                        {/* Formations */}
                        {result.formations?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Formations :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.formations.map((f, index) => (
                                        <li key={index}>
                                            {f.etablissement} - {f.dates}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Expériences */}
                        {result.experiences?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Expériences :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.experiences.map((exp, index) => (
                                        <li key={index}>
                                            {exp.entreprise} - {exp.dates}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Compétences */}
                        {result.competences?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Compétences :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.competences.map((comp, index) => (
                                        <li key={index}>{comp}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Langues */}
                        {result.langues?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Langues :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.langues.map((lang, index) => (
                                        <li key={index}>{lang}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Emails */}
                        {result.emails?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Emails détectés :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.emails.map((email, index) => (
                                        <li key={index}>{email}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Téléphones */}
                        {result.telephones?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Téléphones détectés :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.telephones.map((tel, index) => (
                                        <li key={index}>{tel}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Adresses */}
                        {result.adresses?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Adresses détectées :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.adresses.map((adresse, index) => (
                                        <li key={index}>{adresse}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Dates */}
                        {result.dates?.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-gray-700">Dates extraites :</h4>
                                <ul className="list-disc list-inside space-y-1 text-gray-600">
                                    {result.dates.map((date, index) => (
                                        <li key={index}>{date}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CVUploader;

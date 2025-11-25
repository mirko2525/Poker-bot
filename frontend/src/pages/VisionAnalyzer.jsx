import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';

/**
 * VISION ANALYZER - Pagina upload screenshot poker
 * 
 * File separato e pulito per analisi manuale con Gemini Vision.
 * Utente carica screenshot → AI analizza → Mostra risultati
 */
const VisionAnalyzer = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      
      // Avvia analisi automaticamente
      await analyzeFile(file);
    }
  };
  
  const analyzeFile = async (file) => {
    setAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const API_URL = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${API_URL}/api/vision/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Errore HTTP: ${response.status}`);
      }

      const data = await response.json();
      setResult(data.analysis);
    } catch (err) {
      setError(err.message || 'Errore durante l\'analisi');
      console.error('Errore analisi:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  // Rimosso handleAnalyze - ora l'analisi parte automaticamente

  const getActionColor = (action) => {
    const colors = {
      'FOLD': 'text-red-500',
      'CALL': 'text-yellow-500',
      'CHECK': 'text-blue-500',
      'RAISE': 'text-green-500',
    };
    return colors[action] || 'text-white';
  };

  const getActionBgColor = (action) => {
    const colors = {
      'FOLD': 'bg-red-500/20 border-red-500',
      'CALL': 'bg-yellow-500/20 border-yellow-500',
      'CHECK': 'bg-blue-500/20 border-blue-500',
      'RAISE': 'bg-green-500/20 border-green-500',
    };
    return colors[action] || 'bg-gray-500/20 border-gray-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 py-8 px-4">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-white flex items-center justify-center gap-3">
            <span>🧠</span>
            <span>Vision AI Analyzer</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Carica uno screenshot di PokerStars e lascia che l'AI lo analizzi
          </p>
          <p className="text-sm text-gray-500">
            Powered by Gemini 2.0 Flash Vision
          </p>
        </div>

        {/* Upload Section */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <span>📸</span>
              <span>1. Carica Screenshot</span>
            </CardTitle>
            <CardDescription>
              Seleziona un'immagine del tavolo poker (PNG, JPG)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors flex items-center gap-2"
              >
                <span>📁</span>
                <span>Scegli File</span>
              </label>
              {selectedFile && (
                <span className="text-gray-300 text-sm">
                  {selectedFile.name}
                </span>
              )}
            </div>

            {previewUrl && (
              <div className="border border-gray-700 rounded-lg overflow-hidden">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="w-full h-auto max-h-96 object-contain bg-gray-900"
                />
              </div>
            )}

            {analyzing && (
              <div className="flex items-center justify-center gap-3 bg-blue-600/20 border border-blue-500 rounded-lg p-6">
                <span className="animate-spin text-3xl">⏳</span>
                <span className="text-xl text-blue-400 font-semibold">Analisi AI in corso...</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Error */}
        {error && (
          <Card className="bg-red-900/20 border-red-500">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-400">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Carte Riconosciute */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <span>🎴</span>
                  <span>Carte Riconosciute</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Hero:</div>
                  <div className="flex gap-2">
                    {result.hero_cards && result.hero_cards.length > 0 ? (
                      result.hero_cards.map((card, i) => (
                        <div key={i} className="bg-white text-black px-4 py-2 rounded font-bold text-lg">
                          {card}
                        </div>
                      ))
                    ) : (
                      <span className="text-gray-500">Nessuna carta riconosciuta</span>
                    )}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Board ({result.street}):</div>
                  <div className="flex gap-2">
                    {result.board_cards && result.board_cards.length > 0 ? (
                      result.board_cards.map((card, i) => (
                        <div key={i} className="bg-white text-black px-4 py-2 rounded font-bold text-lg">
                          {card}
                        </div>
                      ))
                    ) : (
                      <span className="text-gray-500">Board vuoto (Preflop)</span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Azione Consigliata */}
            <Card className={`border-2 ${getActionBgColor(result.recommended_action)}`}>
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <span>🎯</span>
                  <span>Azione Consigliata</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-5xl font-bold text-center py-4 ${getActionColor(result.recommended_action)}`}>
                  {result.recommended_action}
                  {result.recommended_action === 'RAISE' && result.recommended_amount > 0 && (
                    <span className="text-3xl ml-2">
                      ${result.recommended_amount.toFixed(2)}
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-gray-800/50 border-gray-700">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-sm text-gray-400 mb-1">Equity Stimata</div>
                    <div className="text-3xl font-bold text-green-400">
                      {(result.equity_estimate * 100).toFixed(1)}%
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gray-800/50 border-gray-700">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-sm text-gray-400 mb-1">Confidenza AI</div>
                    <div className="text-3xl font-bold text-blue-400">
                      {(result.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Game Info */}
            {(result.hero_stack || result.pot_size || result.to_call) && (
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <span>💰</span>
                    <span>Situazione Tavolo</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    {result.hero_stack > 0 && (
                      <div>
                        <div className="text-sm text-gray-400">Stack Hero</div>
                        <div className="text-xl font-bold text-white">
                          ${result.hero_stack.toFixed(2)}
                        </div>
                      </div>
                    )}
                    {result.pot_size > 0 && (
                      <div>
                        <div className="text-sm text-gray-400">Pot</div>
                        <div className="text-xl font-bold text-white">
                          ${result.pot_size.toFixed(2)}
                        </div>
                      </div>
                    )}
                    {result.to_call >= 0 && (
                      <div>
                        <div className="text-sm text-gray-400">To Call</div>
                        <div className="text-xl font-bold text-white">
                          ${result.to_call.toFixed(2)}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* AI Comment */}
            <Card className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 border-blue-500">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <span>🤖</span>
                  <span>Analisi AI</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-200 leading-relaxed italic">
                  {result.ai_comment}
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default VisionAnalyzer;

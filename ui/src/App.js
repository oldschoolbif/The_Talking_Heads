import React, { useState, useEffect } from 'react';
import './App.css';
import ScriptSelector from './components/ScriptSelector';
import ScriptEditor from './components/ScriptEditor';
import PersonaSelector from './components/PersonaSelector';
import ConfigurationPanel from './components/ConfigurationPanel';
import VideoGenerator from './components/VideoGenerator';
import { getScripts, getPersonas, getConfig, updateConfig } from './services/api';

function App() {
  const [selectedScript, setSelectedScript] = useState(null);
  const [scriptContent, setScriptContent] = useState('');
  const [selectedPersonas, setSelectedPersonas] = useState([]);
  const [config, setConfig] = useState({
    avatar: { engine: 'heygen', resolution: { width: 1280, height: 720 } },
    video: { quality: 'high' },
    webhook: { enabled: true, port: 5000 }
  });
  const [personas, setPersonas] = useState([]);
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const [error, setError] = useState(null);
  const [errorDismissed, setErrorDismissed] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      setErrorDismissed(false); // Reset error dismissed when refreshing
      const [scriptsData, personasData, configData] = await Promise.all([
        getScripts().catch(err => {
          console.error('Error loading scripts:', err);
          return [];
        }),
        getPersonas().catch(err => {
          console.error('Error loading personas:', err);
          return [];
        }),
        getConfig().catch(err => {
          console.error('Error loading config:', err);
          return {
            avatar: { engine: 'heygen', resolution: { width: 1280, height: 720 } },
            video: { quality: 'high' },
            webhook: { enabled: true, port: 5000 }
          };
        })
      ]);
      setScripts(scriptsData || []);
      setPersonas(personasData || []);
      setConfig(configData || {
        avatar: { engine: 'heygen', resolution: { width: 1280, height: 720 } },
        video: { quality: 'high' },
        webhook: { enabled: true, port: 5000 }
      });
      
      // Debug logging
      console.log('Loaded scripts:', scriptsData?.length || 0);
      console.log('Loaded personas:', personasData?.length || 0);
      if (personasData && personasData.length > 0) {
        console.log('Personas:', personasData.map(p => p.name || p.key));
      }
      
      if ((!scriptsData || scriptsData.length === 0) && (!personasData || personasData.length === 0)) {
        // Don't show error if data is empty - might be intentional
        console.warn('No scripts or personas loaded');
      }
    } catch (error) {
      console.error('Error loading data:', error);
      // Only show error banner if it's a connection issue
      if (error.message?.includes('connect') || error.message?.includes('timeout') || error.message?.includes('server')) {
        setError(error.message);
      } else {
        // For other errors, just log them
        console.error('Non-critical error loading data:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleScriptSelect = (script) => {
    setSelectedScript(script);
    setScriptContent(script.content || '');
  };

  const handleConfigUpdate = async (newConfig) => {
    try {
      await updateConfig(newConfig);
      setConfig(newConfig);
    } catch (error) {
      console.error('Error updating config:', error);
    }
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🎬 The Talking Heads</h1>
            <p>AI Video Generation Studio</p>
          </div>
          <button className="btn btn-secondary btn-small" onClick={loadData} title="Refresh data">
            🔄 Refresh
          </button>
        </div>
      </header>
      
      {error && !errorDismissed && (
        <div className="app-error-banner">
          <span>
            <span className="error-icon">⚠️</span>
            <span className="error-message">{error}</span>
          </span>
          <button 
            onClick={() => {
              setError(null);
              setErrorDismissed(true);
            }}
            title="Dismiss error"
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      <main className="app-main">
        <div className="app-grid">
          {/* Left Column - Script Selection, Script Editor & Personas */}
          <div className="app-column left-column">
            <ScriptSelector
              scripts={scripts}
              selectedScript={selectedScript}
              onSelect={handleScriptSelect}
            />
            
            {selectedScript && (
              <ScriptEditor
                script={selectedScript}
                content={scriptContent}
                onChange={setScriptContent}
                personas={selectedPersonas}
              />
            )}

            <PersonaSelector
              personas={personas}
              selectedPersonas={selectedPersonas}
              onSelect={setSelectedPersonas}
              maxSelection={5}
            />
          </div>

          {/* Right Column - Configuration & Generation (full width) */}
          <div className="app-column right-column">
            <ConfigurationPanel
              config={config}
              onUpdate={handleConfigUpdate}
            />

            <VideoGenerator
              script={selectedScript}
              scriptContent={scriptContent}
              selectedPersonas={selectedPersonas}
              config={config}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;


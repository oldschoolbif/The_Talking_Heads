import React, { useState, useEffect } from 'react';
import './PersonaSelector.css';
import { generateVoiceSample, getAvatarImage } from '../services/api';

function PersonaSelector({ personas, selectedPersonas, onSelect, maxSelection = 5 }) {
  const [voiceSamples, setVoiceSamples] = useState({});
  const [avatarImages, setAvatarImages] = useState({});
  const [loadingSamples, setLoadingSamples] = useState({});

  const handlePersonaToggle = (persona) => {
    if (selectedPersonas.find(p => p.key === persona.key)) {
      // Deselect
      onSelect(selectedPersonas.filter(p => p.key !== persona.key));
    } else {
      // Select (if under limit)
      if (selectedPersonas.length < maxSelection) {
        onSelect([...selectedPersonas, persona]);
      }
    }
  };

  const loadVoiceSample = async (persona) => {
    if (voiceSamples[persona.key] || loadingSamples[persona.key]) return;
    
    try {
      setLoadingSamples(prev => ({ ...prev, [persona.key]: true }));
      const sample = await generateVoiceSample(persona.key);
      setVoiceSamples(prev => ({ ...prev, [persona.key]: sample.audio_url }));
    } catch (error) {
      console.error(`Error loading voice sample for ${persona.key}:`, error);
    } finally {
      setLoadingSamples(prev => ({ ...prev, [persona.key]: false }));
    }
  };

  const loadAvatarImage = async (persona) => {
    if (avatarImages[persona.key]) return;
    
    try {
      const avatarId = persona.avatar?.avatar_id;
      const engine = persona.avatar?.engine || 'heygen';
      if (avatarId) {
        const image = await getAvatarImage(avatarId, engine);
        if (image?.image_url) {
          setAvatarImages(prev => ({ ...prev, [persona.key]: image.image_url }));
        }
      }
    } catch (error) {
      // Silently handle avatar image errors - they're not critical
      // Use a placeholder instead
      setAvatarImages(prev => ({ ...prev, [persona.key]: null }));
    }
  };

  useEffect(() => {
    // Load avatar images for all personas
    personas.forEach(persona => {
      loadAvatarImage(persona);
    });
  }, [personas]);

  return (
    <div className="panel persona-selector">
      <div className="panel-header">
        <h2>👥 Personas ({selectedPersonas.length}/{maxSelection})</h2>
        <p className="panel-subtitle">Step 3: Select personas with previews</p>
      </div>

      <div className="persona-list">
        {personas.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">👥</div>
            <p>No personas found</p>
            <p className="empty-state-hint">Personas should be configured in config/personas.yaml</p>
          </div>
        ) : (
          personas.map((persona) => {
            const isSelected = selectedPersonas.find(p => p.key === persona.key);
            const voiceUrl = voiceSamples[persona.key];
            const avatarUrl = avatarImages[persona.key];
            const isLoading = loadingSamples[persona.key];

            return (
              <div
                key={persona.key}
                className={`persona-card ${isSelected ? 'selected' : ''}`}
                onClick={() => handlePersonaToggle(persona)}
              >
                <div className="persona-avatar">
                  {avatarUrl ? (
                    <img src={avatarUrl} alt={persona.name} />
                  ) : (
                    <div className="avatar-placeholder">
                      <span>{persona.name.charAt(0)}</span>
                    </div>
                  )}
                  {isSelected && (
                    <div className="selected-badge">✓</div>
                  )}
                </div>

                <div className="persona-info">
                  <h3>{persona.name}</h3>
                  <p className="persona-description">{persona.description}</p>

                  <div className="persona-details">
                    <div className="persona-detail">
                      <span className="detail-label">Voice:</span>
                      <span className="detail-value">{persona.voice?.engine || 'N/A'}</span>
                    </div>
                    <div className="persona-detail">
                      <span className="detail-label">Avatar:</span>
                      <span className="detail-value">{persona.avatar?.engine || 'N/A'}</span>
                    </div>
                  </div>

                  <div className="persona-voice-sample">
                    {voiceUrl ? (
                      <audio controls>
                        <source src={voiceUrl} type="audio/mpeg" />
                        Your browser does not support audio.
                      </audio>
                    ) : (
                      <button
                        className="btn btn-secondary btn-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          loadVoiceSample(persona);
                        }}
                        disabled={isLoading}
                      >
                        {isLoading ? 'Loading...' : '▶ Preview Voice'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {selectedPersonas.length > 0 && (
        <div className="selected-personas-summary">
          <h4>Selected Personas:</h4>
          <div className="selected-tags">
            {selectedPersonas.map((persona) => (
              <span key={persona.key} className="persona-tag">
                {persona.name}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePersonaToggle(persona);
                  }}
                  className="tag-remove"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default PersonaSelector;


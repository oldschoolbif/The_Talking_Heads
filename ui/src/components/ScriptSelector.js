import React from 'react';
import './ScriptSelector.css';

function ScriptSelector({ scripts, selectedScript, onSelect }) {
  return (
    <div className="panel script-selector">
      <div className="panel-header">
        <h2>📄 Script Selection</h2>
        <p className="panel-subtitle">Step 1: Choose your script</p>
      </div>
      
      <div className="script-list">
        {scripts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📄</div>
            <p>No scripts found</p>
            <p className="empty-state-hint">Scripts should be in examples/scripts/ folder</p>
          </div>
        ) : (
          scripts.map((script) => (
            <div
              key={script.filename}
              className={`script-item ${selectedScript?.filename === script.filename ? 'active' : ''}`}
              onClick={() => onSelect(script)}
            >
              <div className="script-item-header">
                <h3>{script.name || script.filename}</h3>
                <span className="script-date">{new Date(script.modified).toLocaleDateString()}</span>
              </div>
              <p className="script-preview">{script.preview}</p>
              <div className="script-meta">
                <span className="script-segments">{script.segments || 0} segments</span>
                <span className="script-personas">{script.personas?.length || 0} personas</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ScriptSelector;


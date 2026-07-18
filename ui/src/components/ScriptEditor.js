import React, { useState } from 'react';
import './ScriptEditor.css';

const AVAILABLE_TAGS = [
  { tag: '[expression:happy]', description: 'Happy expression' },
  { tag: '[expression:neutral]', description: 'Neutral expression' },
  { tag: '[expression:surprised]', description: 'Surprised expression' },
  { tag: '[gesture:point]', description: 'Pointing gesture' },
  { tag: '[gesture:wave]', description: 'Waving gesture' },
  { tag: '[gesture:emphasize]', description: 'Emphasis gesture' },
  { tag: '[pause:2]', description: '2 second pause' },
  { tag: '[pause:3]', description: '3 second pause' },
];

function ScriptEditor({ script, content, onChange, personas }) {
  const [showTags, setShowTags] = useState(false);

  const insertTag = (tag) => {
    const textarea = document.querySelector('.script-textarea');
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newContent = content.substring(0, start) + tag + ' ' + content.substring(end);
      onChange(newContent);
      // Set cursor position after tag
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + tag.length + 1, start + tag.length + 1);
      }, 0);
    }
  };

  const formatScriptPreview = () => {
    if (!content) return '';
    
    // Show formatted preview with persona highlights
    return content.split('\n').map((line, idx) => {
      const match = line.match(/^(\w+):\s*(.+)$/);
      if (match) {
        const [, persona, text] = match;
        const isSelected = personas.some(p => p.key.toLowerCase() === persona.toLowerCase());
        return (
          <div key={idx} className={`script-line ${isSelected ? 'persona-selected' : ''}`}>
            <span className="persona-tag">{persona}:</span>
            <span className="script-text">{text}</span>
          </div>
        );
      }
      return <div key={idx} className="script-line">{line}</div>;
    });
  };

  return (
    <div className="panel script-editor">
      <div className="panel-header">
        <h2>✏️ Script Editor</h2>
        {script && <span className="script-filename">{script.filename}</span>}
      </div>

      <div className="editor-toolbar">
        <button
          className="btn btn-secondary"
          onClick={() => setShowTags(!showTags)}
        >
          {showTags ? '▼' : '▶'} Tags & Formatting
        </button>
        <button className="btn btn-secondary" onClick={() => onChange('')}>
          Clear
        </button>
      </div>

      {showTags && (
        <div className="tags-panel">
          <h4>Available Tags:</h4>
          <div className="tags-list">
            {AVAILABLE_TAGS.map((item, idx) => (
              <div
                key={idx}
                className="tag-item"
                onClick={() => insertTag(item.tag)}
                title={item.description}
              >
                <code>{item.tag}</code>
                <span className="tag-description">{item.description}</span>
              </div>
            ))}
          </div>
          <div className="script-format-help">
            <h4>Format:</h4>
            <pre>{`PERSONA: Dialogue text here
[expression:happy] [gesture:point] Optional tags before text
[pause:2] Pause tags create delays

Example:
ALICE: Welcome to our show! [expression:happy]
BOB: Thanks for having me. [gesture:wave]`}</pre>
          </div>
        </div>
      )}

      <div className="editor-container">
        <textarea
          className="script-textarea textarea"
          value={content}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Enter your script here...

Format:
PERSONA: Dialogue text
[expression:type] Optional tags
[gesture:type] More tags
[pause:seconds] Pause tags

Example:
ALICE: Hello everyone! [expression:happy] [gesture:wave]
BOB: Hi Alice! [gesture:point]"
        />
        
        <div className="script-preview-panel">
          <h4>Preview:</h4>
          <div className="script-preview-content">
            {formatScriptPreview()}
          </div>
        </div>
      </div>

      <div className="editor-stats">
        <span>Lines: {content.split('\n').length}</span>
        <span>Characters: {content.length}</span>
        <span>Segments: {content.split('\n').filter(l => l.match(/^\w+:/)).length}</span>
      </div>
    </div>
  );
}

export default ScriptEditor;


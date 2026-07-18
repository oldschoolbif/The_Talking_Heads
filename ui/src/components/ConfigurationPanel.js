import React, { useState } from 'react';
import './ConfigurationPanel.css';

const RESOLUTION_PRESETS = [
  { label: '720p (Fast)', width: 1280, height: 720, description: 'Faster processing, good quality' },
  { label: '1080p (Quality)', width: 1920, height: 1080, description: 'Best quality, slower processing' },
  { label: 'Custom', width: null, height: null, description: 'Set custom dimensions' },
];

const QUALITY_PRESETS = [
  { value: 'fastest', label: 'Fastest', description: 'Lowest quality, fastest generation' },
  { value: 'fast', label: 'Fast', description: 'Good balance of speed and quality' },
  { value: 'medium', label: 'Medium', description: 'Balanced quality and speed' },
  { value: 'high', label: 'High (Recommended)', description: 'Best quality, slower generation' },
];

const AVATAR_ENGINES = [
  { value: 'dreamtalk', label: 'DreamTalk (Local GPU)', description: 'Highest quality, runs locally on GPU, no API costs' },
  { value: 'heygen', label: 'HeyGen', description: 'High quality cloud API, supports expressions & gestures' },
  { value: 'did', label: 'D-ID', description: 'Fast cloud API generation, good for simple videos' },
];

const TTS_ENGINES = [
  { value: 'xtts', label: 'XTTS-v3 (Local GPU)', description: 'Highest quality, voice cloning, runs locally on GPU, no API costs' },
  { value: 'bark', label: 'Bark (Local GPU)', description: 'Expressive TTS with music/sound effects, runs locally on GPU' },
  { value: 'valle', label: 'VALL-E X (Local GPU)', description: 'Research-grade quality, zero-shot voice cloning, runs locally' },
  { value: 'elevenlabs', label: 'ElevenLabs (External - Subscription Required)', description: 'Cloud API, requires subscription and API key setup' },
  { value: 'azure', label: 'Azure Speech (External - Subscription Required)', description: 'Microsoft cloud API, requires subscription and API key setup' },
];

function ConfigurationPanel({ config, onUpdate }) {
  const [errors, setErrors] = useState({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  const validateAndUpdate = (path, value, validator) => {
    const errorKey = path.replace(/\./g, '_');
    
    if (validator) {
      const error = validator(value);
      if (error) {
        setErrors(prev => ({ ...prev, [errorKey]: error }));
        return;
      } else {
        setErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors[errorKey];
          return newErrors;
        });
      }
    }
    
    updateConfig(path, value);
  };

  const updateConfig = (path, value) => {
    const newConfig = { ...config };
    const keys = path.split('.');
    let current = newConfig;
    
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) current[keys[i]] = {};
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    onUpdate(newConfig);
  };

  const handleResolutionPreset = (preset) => {
    if (preset.width && preset.height) {
      updateConfig('avatar.resolution.width', preset.width);
      updateConfig('avatar.resolution.height', preset.height);
    }
  };

  const validateWidth = (value) => {
    const num = parseInt(value);
    if (isNaN(num)) return 'Width must be a number';
    if (num < 480) return 'Width must be at least 480px';
    if (num > 3840) return 'Width cannot exceed 3840px';
    if (num % 16 !== 0) return 'Width should be divisible by 16 for best results';
    return null;
  };

  const validateHeight = (value) => {
    const num = parseInt(value);
    if (isNaN(num)) return 'Height must be a number';
    if (num < 270) return 'Height must be at least 270px';
    if (num > 2160) return 'Height cannot exceed 2160px';
    if (num % 16 !== 0) return 'Height should be divisible by 16 for best results';
    return null;
  };

  const validateFPS = (value) => {
    const num = parseInt(value);
    if (isNaN(num)) return 'FPS must be a number';
    if (num < 15) return 'FPS must be at least 15';
    if (num > 60) return 'FPS cannot exceed 60';
    return null;
  };

  const validatePort = (value) => {
    const num = parseInt(value);
    if (isNaN(num)) return 'Port must be a number';
    if (num < 1024) return 'Port must be at least 1024';
    if (num > 65535) return 'Port cannot exceed 65535';
    return null;
  };

  const currentResolution = config.avatar?.resolution || { width: 1280, height: 720 };
  const currentPreset = RESOLUTION_PRESETS.find(
    p => p.width === currentResolution.width && p.height === currentResolution.height
  ) || RESOLUTION_PRESETS[2];

  return (
    <div className="panel configuration-panel">
      <div className="panel-header">
        <h2>⚙️ Configuration</h2>
        <p className="panel-subtitle">Configure video generation settings</p>
      </div>

      <div className="config-sections">
        {/* TTS Engine - Step 3 in workflow */}
        <div className="config-section config-section-primary">
          <div className="config-section-header">
            <h3>🎤 TTS Engine</h3>
            <span className="config-badge">Step 3</span>
          </div>
          <div className="form-group">
            <label className="label">Text-to-Speech Provider</label>
            <select
              className="select"
              value={config.tts?.engine || 'xtts'}
              onChange={(e) => updateConfig('tts.engine', e.target.value)}
            >
              {TTS_ENGINES.map(engine => (
                <option key={engine.value} value={engine.value}>
                  {engine.label} - {engine.description}
                </option>
              ))}
            </select>
            <p className="field-hint">Choose the text-to-speech provider (local GPU options first, external APIs last)</p>
          </div>
        </div>

        {/* Avatar Engine - Step 4 in workflow */}
        <div className="config-section config-section-primary">
          <div className="config-section-header">
            <h3>🎭 Avatar Engine</h3>
            <span className="config-badge">Step 4</span>
          </div>
          <div className="form-group">
            <label className="label">Provider</label>
            <select
              className="select"
              value={config.avatar?.engine || 'dreamtalk'}
              onChange={(e) => updateConfig('avatar.engine', e.target.value)}
            >
              {AVATAR_ENGINES.map(engine => (
                <option key={engine.value} value={engine.value}>
                  {engine.label} - {engine.description}
                </option>
              ))}
            </select>
            <p className="field-hint">Choose the avatar generation provider</p>
          </div>
        </div>

        {/* Resolution & Attributes - Step 5 in workflow */}
        <div className="config-section config-section-primary">
          <div className="config-section-header">
            <h3>📐 Resolution & Attributes</h3>
            <span className="config-badge">Step 5</span>
          </div>
          
          <div className="form-group">
            <label className="label">Preset</label>
            <select
              className="select"
              value={currentPreset.label}
              onChange={(e) => {
                const preset = RESOLUTION_PRESETS.find(p => p.label === e.target.value);
                if (preset) handleResolutionPreset(preset);
              }}
            >
              {RESOLUTION_PRESETS.map(preset => (
                <option key={preset.label} value={preset.label}>
                  {preset.label} - {preset.description}
                </option>
              ))}
            </select>
            <p className="field-hint">{currentPreset.description}</p>
          </div>
          
          <div className="grid-2">
            <div className="form-group">
              <label className="label">
                Width (px)
                {errors.avatar_resolution_width && (
                  <span className="error-text"> - {errors.avatar_resolution_width}</span>
                )}
              </label>
              <input
                type="number"
                className={`input ${errors.avatar_resolution_width ? 'input-error' : ''}`}
                value={currentResolution.width || 1280}
                onChange={(e) => validateAndUpdate(
                  'avatar.resolution.width',
                  parseInt(e.target.value) || 1280,
                  validateWidth
                )}
                min="480"
                max="3840"
                step="16"
              />
            </div>
            <div className="form-group">
              <label className="label">
                Height (px)
                {errors.avatar_resolution_height && (
                  <span className="error-text"> - {errors.avatar_resolution_height}</span>
                )}
              </label>
              <input
                type="number"
                className={`input ${errors.avatar_resolution_height ? 'input-error' : ''}`}
                value={currentResolution.height || 720}
                onChange={(e) => validateAndUpdate(
                  'avatar.resolution.height',
                  parseInt(e.target.value) || 720,
                  validateHeight
                )}
                min="270"
                max="2160"
                step="16"
              />
            </div>
          </div>
          <div className="resolution-preview">
            <span className="preview-label">Preview:</span>
            <span className="preview-value">
              {currentResolution.width}x{currentResolution.height}
            </span>
          </div>
          
          {/* Quality Settings - inline with resolution */}
          <div className="form-group" style={{ marginTop: '16px' }}>
            <label className="label">Video Quality</label>
            <select
              className="select"
              value={config.video?.quality || 'high'}
              onChange={(e) => updateConfig('video.quality', e.target.value)}
            >
              {QUALITY_PRESETS.map(quality => (
                <option key={quality.value} value={quality.value}>
                  {quality.label} - {quality.description}
                </option>
              ))}
            </select>
            <p className="field-hint">Affects processing speed and output quality</p>
          </div>
        </div>


        {/* Advanced Settings Toggle */}
        <div className="config-section-advanced-toggle">
          <button
            className="btn btn-secondary btn-small"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? '▼ Hide' : '▶ Show'} Advanced Settings
          </button>
        </div>

        {/* Advanced Settings */}
        {showAdvanced && (
          <>
            {/* Output Settings */}
            <div className="config-section config-section-advanced">
              <h3>📹 Output Settings</h3>
              <div className="form-group">
                <label className="label">Output Format</label>
                <select
                  className="select"
                  value={config.video?.format || 'mp4'}
                  onChange={(e) => updateConfig('video.format', e.target.value)}
                >
                  <option value="mp4">MP4 (Recommended)</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="label">
                  FPS (Frames Per Second)
                  {errors.video_fps && (
                    <span className="error-text"> - {errors.video_fps}</span>
                  )}
                </label>
                <input
                  type="number"
                  className={`input ${errors.video_fps ? 'input-error' : ''}`}
                  value={config.video?.fps || config.avatar?.fps || 30}
                  onChange={(e) => validateAndUpdate(
                    'video.fps',
                    parseInt(e.target.value) || 30,
                    validateFPS
                  )}
                  min="15"
                  max="60"
                  step="5"
                />
                <p className="field-hint">Standard: 30 FPS, Smooth: 60 FPS</p>
              </div>
            </div>

            {/* Webhook Settings */}
            <div className="config-section config-section-advanced">
              <h3>🔔 Webhook Settings</h3>
              <div className="form-group">
                <label className="label checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.webhook?.enabled !== false}
                    onChange={(e) => updateConfig('webhook.enabled', e.target.checked)}
                  />
                  <span>Enable Webhooks (faster notifications)</span>
                </label>
                <p className="field-hint">Receive real-time updates when videos are ready</p>
              </div>
              
              {config.webhook?.enabled !== false && (
                <div className="form-group">
                  <label className="label">
                    Webhook Port
                    {errors.webhook_port && (
                      <span className="error-text"> - {errors.webhook_port}</span>
                    )}
                  </label>
                  <input
                    type="number"
                    className={`input ${errors.webhook_port ? 'input-error' : ''}`}
                    value={config.webhook?.port || 5000}
                    onChange={(e) => validateAndUpdate(
                      'webhook.port',
                      parseInt(e.target.value) || 5000,
                      validatePort
                    )}
                    min="1024"
                    max="65535"
                  />
                  <p className="field-hint">Port for receiving webhook callbacks</p>
                </div>
              )}
            </div>
          </>
        )}

        {/* Current Settings Summary - Always Visible */}
        <div className="config-summary">
          <h4>📋 Current Settings Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Resolution</span>
              <span className="summary-value">
                {currentResolution.width}x{currentResolution.height}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Engine</span>
              <span className="summary-value">
                {AVATAR_ENGINES.find(e => e.value === (config.avatar?.engine || 'dreamtalk'))?.label || 'DreamTalk'}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Quality</span>
              <span className="summary-value">
                {QUALITY_PRESETS.find(q => q.value === (config.video?.quality || 'high'))?.label || 'High'}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">FPS</span>
              <span className="summary-value">{config.video?.fps || config.avatar?.fps || 30}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConfigurationPanel;

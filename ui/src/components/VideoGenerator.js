import React, { useState, useEffect } from 'react';
import './VideoGenerator.css';
import { generateVideo, getVideoStatus } from '../services/api';

function VideoGenerator({ script, scriptContent, selectedPersonas, config }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [statusLog, setStatusLog] = useState([]);

  useEffect(() => {
    let interval = null;
    if (isGenerating && generationStatus?.job_id) {
      interval = setInterval(async () => {
        try {
          const status = await getVideoStatus(generationStatus.job_id);
          console.log(`[Status Poll] Job ${generationStatus.job_id?.substring(0, 8)}: ${status.status}, progress: ${status.progress}%`);
          
          // Preserve job_id and reset error counters on successful response
          const currentStatus = generationStatus || {};
          setGenerationStatus({ 
            ...status, 
            job_id: currentStatus.job_id || status.job_id,
            consecutive_404s: 0,        // Reset on success
            network_errors_count: 0,    // Reset on success
            other_errors_count: 0       // Reset on success
          });
          // Always update progress from the status response, but never go backwards
          const newProgress = status.progress || 0;
          setProgress(prevProgress => Math.max(prevProgress, newProgress)); // Never decrease
          if (newProgress > (progress || 0)) {
            console.log(`[Status Poll] Updated progress to ${newProgress}%`);
          }
          
          if (status.log_entries) {
            setStatusLog(status.log_entries);
          }
          
          if (status.status === 'completed') {
            setIsGenerating(false);
            setVideoUrl(status.video_url);
            if (interval) clearInterval(interval);
          } else if (status.status === 'failed') {
            setIsGenerating(false);
            setError(status.error || 'Video generation failed');
            if (interval) clearInterval(interval);
          }
        } catch (err) {
          // Handle errors more gracefully - don't stop on single failures
          if (err.response?.status === 404 || err.message?.includes('Job not found')) {
            // Job not found - could be backend restart or job completed/cleaned up
            // Only stop after multiple consecutive 404s to avoid false positives
            const currentStatus = generationStatus || {};
            const consecutive404s = (currentStatus.consecutive_404s || 0) + 1;
            setGenerationStatus({ ...currentStatus, consecutive_404s });
            
            if (consecutive404s >= 3) {
              // After 3 consecutive 404s (9 seconds), assume job is lost
              setIsGenerating(false);
              setError('Generation job was lost (backend may have restarted). Please start a new generation.');
              if (interval) clearInterval(interval);
            } else {
              // Temporary 404 - keep trying
              console.warn(`[Status Poll] Job not found (attempt ${consecutive404s}/3), will retry...`);
            }
          } else if (err.message?.includes('Network error') || err.message?.includes('refresh') || err.message?.includes('CORS')) {
            // Network/CORS errors - retry a few times before giving up
            const currentStatus = generationStatus || {};
            const networkErrorsCount = (currentStatus.network_errors_count || 0) + 1;
            setGenerationStatus({ ...currentStatus, network_errors_count: networkErrorsCount });
            
            if (networkErrorsCount >= 5) {
              // After 5 consecutive network errors (15 seconds), give up
              setIsGenerating(false);
              setError('Network error. Please check your connection and refresh the page.');
              if (interval) clearInterval(interval);
            } else {
              // Temporary network issue - keep trying
              console.warn(`[Status Poll] Network error (attempt ${networkErrorsCount}/5), will retry...`);
            }
          } else {
            // Other errors - log but don't stop immediately
            console.error('Error checking status:', err);
            const currentStatus = generationStatus || {};
            const otherErrorsCount = (currentStatus.other_errors_count || 0) + 1;
            setGenerationStatus({ ...currentStatus, other_errors_count: otherErrorsCount });
            
            if (otherErrorsCount >= 10) {
              // After 10 consecutive errors (30 seconds), give up
              setIsGenerating(false);
              setError('Multiple errors occurred. Please try starting a new generation.');
              if (interval) clearInterval(interval);
            }
          }
        }
      }, 3000); // Check every 3 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isGenerating, generationStatus]);

  const validateGeneration = () => {
    const errors = [];
    
    if (!script) {
      errors.push('Please select a script');
    }
    
    if (!scriptContent || scriptContent.trim().length === 0) {
      errors.push('Script content cannot be empty');
    } else if (scriptContent.trim().length < 10) {
      errors.push('Script content is too short (minimum 10 characters)');
    }
    
    if (selectedPersonas.length === 0) {
      errors.push('Please select at least one persona');
    } else if (selectedPersonas.length > 5) {
      errors.push('Maximum 5 personas allowed');
    }
    
    // Check if script content matches selected personas
    if (scriptContent && selectedPersonas.length > 0) {
      const scriptPersonas = scriptContent.match(/([A-Z_]+):/g)?.map(p => p.replace(':', '')) || [];
      const selectedKeys = selectedPersonas.map(p => p.key.toUpperCase());
      const missingPersonas = scriptPersonas.filter(p => !selectedKeys.includes(p));
      
      if (missingPersonas.length > 0) {
        errors.push(`Script references personas not selected: ${missingPersonas.join(', ')}`);
      }
    }
    
    return errors;
  };

  const handleGenerate = async () => {
    const validationErrors = validateGeneration();
    
    if (validationErrors.length > 0) {
      setError(validationErrors.join('. '));
      return;
    }

    try {
      setError(null);
      setIsGenerating(true);
      setProgress(0);
      setStatusLog([]);
      setVideoUrl(null);

      const result = await generateVideo({
        script_content: scriptContent,
        script_filename: script.filename,
        personas: selectedPersonas.map(p => p.key),
        config: config,
      });

      // Store job_id for polling
      setGenerationStatus({ ...result, job_id: result.job_id });
      setProgress(0);
    } catch (err) {
      setIsGenerating(false);
      const errorMessage = err.response?.data?.error || err.message || 'Failed to start video generation';
      setError(errorMessage);
    }
  };

  const validationErrors = validateGeneration();
  const canGenerate = validationErrors.length === 0 && !isGenerating;

  return (
    <div className="panel video-generator">
      <div className="panel-header">
        <h2>🎬 Generate Video</h2>
        <p className="panel-subtitle">Step 6: Verify requirements and generate</p>
      </div>

      {/* Validation Summary */}
      <div className="generation-validation">
        <h4>Requirements Checklist</h4>
        <div className="validation-list">
          <div className={`validation-item ${script ? 'valid' : 'invalid'}`}>
            <span className="validation-icon">{script ? '✓' : '✗'}</span>
            <span className="validation-text">Script Selected</span>
            {script && <span className="validation-detail">{script.filename}</span>}
          </div>
          <div className={`validation-item ${scriptContent && scriptContent.trim().length >= 10 ? 'valid' : 'invalid'}`}>
            <span className="validation-icon">{scriptContent && scriptContent.trim().length >= 10 ? '✓' : '✗'}</span>
            <span className="validation-text">Script Content</span>
            {scriptContent && (
              <span className="validation-detail">
                {scriptContent.trim().length} characters
                {scriptContent.trim().length < 10 && ' (min 10)'}
              </span>
            )}
          </div>
          <div className={`validation-item ${selectedPersonas.length > 0 && selectedPersonas.length <= 5 ? 'valid' : 'invalid'}`}>
            <span className="validation-icon">{selectedPersonas.length > 0 && selectedPersonas.length <= 5 ? '✓' : '✗'}</span>
            <span className="validation-text">Personas Selected</span>
            <span className="validation-detail">
              {selectedPersonas.length > 0 
                ? `${selectedPersonas.length}/5 ${selectedPersonas.length === 1 ? 'persona' : 'personas'}`
                : 'Select 1-5 personas'}
            </span>
          </div>
        </div>
        {validationErrors.length > 0 && (
          <div className="validation-errors">
            {validationErrors.map((err, idx) => (
              <div key={idx} className="validation-error-item">⚠️ {err}</div>
            ))}
          </div>
        )}
      </div>

      {/* Generation Button */}
      <button
        className="btn btn-primary generate-btn"
        onClick={handleGenerate}
        disabled={!canGenerate}
      >
        {isGenerating ? '⏳ Generating...' : '▶ Generate Video'}
      </button>

      {/* Progress */}
      {isGenerating && (
        <div className="generation-progress">
          <div className="progress-bar-container">
            <div
              className="progress-bar"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="progress-text">{Math.round(progress)}%</div>
        </div>
      )}

      {/* Status Log */}
      {statusLog.length > 0 && (
        <div className="status-log">
          <h4>Status Log</h4>
          <div className="log-entries">
            {statusLog.slice(-10).map((entry, idx) => (
              <div key={idx} className="log-entry">
                <span className="log-time">{entry.timestamp}</span>
                <span className="log-message">{entry.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Video Preview */}
      {videoUrl && (
        <div className="video-preview">
          <h4>Generated Video</h4>
          <video controls src={videoUrl} className="video-player">
            Your browser does not support video playback.
          </video>
          <a
            href={videoUrl}
            download
            className="btn btn-secondary download-btn"
          >
            📥 Download Video
          </a>
        </div>
      )}

      {/* Configuration Summary */}
      {canGenerate && (
        <div className="generation-summary">
          <h4>Generation Summary</h4>
          <div className="summary-details">
            <div className="summary-row">
              <span>Script:</span>
              <span>{script?.filename}</span>
            </div>
            <div className="summary-row">
              <span>Personas:</span>
              <span>{selectedPersonas.map(p => p.name).join(', ')}</span>
            </div>
            <div className="summary-row">
              <span>Resolution:</span>
              <span>
                {config.avatar?.resolution?.width || 1280}x
                {config.avatar?.resolution?.height || 720}
              </span>
            </div>
            <div className="summary-row">
              <span>Engine:</span>
              <span>{config.avatar?.engine || 'heygen'}</span>
            </div>
            <div className="summary-row">
              <span>Quality:</span>
              <span>{config.video?.quality || 'high'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VideoGenerator;


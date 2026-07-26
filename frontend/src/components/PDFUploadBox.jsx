import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertTriangle } from 'lucide-react';
import LiveLoader from './LiveLoader';

const PDFUploadBox = ({ onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [errorMessage, setErrorMessage] = useState('');
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  const validateAndProcessFile = (selectedFile) => {
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setStatus('error');
      setErrorMessage('Please upload a PDF file only.');
      setFile(null);
      return;
    }
    setFile(selectedFile);
    setStatus('idle');
    setErrorMessage('');
  };

  const onButtonClick = () => {
    inputRef.current.click();
  };

  const handleUploadSubmit = async () => {
    if (!file) return;
    
    setStatus('loading');
    try {
      await onUploadSuccess(file);
      setStatus('success');
    } catch (err) {
      console.error(err);
      setStatus('error');
      setErrorMessage(err.response?.data?.detail || 'An error occurred while uploading. Try again.');
    }
  };

  const resetUpload = () => {
    setFile(null);
    setStatus('idle');
    setErrorMessage('');
  };

  return (
    <div className="glass-card" style={{ padding: '2.5rem', width: '100%', maxWidth: '600px', margin: '0 auto' }}>
      <form 
        onDragEnter={handleDrag} 
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onSubmit={(e) => e.preventDefault()}
        style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
      >
        <input 
          ref={inputRef}
          type="file" 
          id="input-file-upload" 
          multiple={false} 
          accept=".pdf"
          onChange={handleChange} 
          style={{ display: 'none' }}
        />
        
        <div 
          className="upload-dropzone" 
          style={{
            borderColor: dragActive ? 'var(--accent-purple)' : 'var(--primary-lavender-dark)',
            backgroundColor: dragActive ? 'rgba(235, 223, 255, 0.4)' : 'rgba(255, 255, 255, 0.5)',
            transform: dragActive ? 'scale(1.01)' : 'scale(1)'
          }}
          onClick={status === 'idle' || status === 'error' ? onButtonClick : undefined}
        >
          {status === 'loading' ? (
            <LiveLoader 
              text="Indexing & extracting vector pages..." 
              size="large" 
              icon="cpu" 
            />
          ) : status === 'success' ? (
            <>
              <CheckCircle2 size={48} style={{ color: 'var(--pastel-green-border)' }} />
              <div>
                <p style={{ fontWeight: 600, fontSize: '1.1rem', color: 'green' }}>Upload Complete!</p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-navy-muted)', marginTop: '4px' }}>Your paper has been simplified. Head over to Chat to query it!</p>
              </div>
            </>
          ) : file ? (
            <>
              <FileText size={48} style={{ color: 'var(--accent-purple)' }} />
              <div>
                <p style={{ fontWeight: 600, fontSize: '1.05rem', wordBreak: 'break-all' }}>{file.name}</p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-navy-muted)' }}>{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              </div>
            </>
          ) : (
            <>
              <Upload size={48} style={{ color: 'var(--text-navy-muted)' }} />
              <div>
                <p style={{ fontWeight: 600, fontSize: '1.1rem' }}>Drag & Drop Research Paper PDF</p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-navy-muted)', marginTop: '4px' }}>or click to browse your computer</p>
              </div>
            </>
          )}
        </div>

        {status === 'error' && (
          <div style={{
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px', 
            background: '#fee2e2', 
            color: '#b91c1c', 
            padding: '12px', 
            borderRadius: '10px',
            fontSize: '0.9rem',
            border: '1px solid #fca5a5'
          }}>
            <AlertTriangle size={18} />
            <span>{errorMessage}</span>
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          {(status === 'success' || file) && (
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={resetUpload}
              disabled={status === 'loading'}
            >
              Reset
            </button>
          )}

          {file && status === 'idle' && (
            <button 
              type="button" 
              className="btn btn-primary" 
              onClick={handleUploadSubmit}
            >
              Process Paper
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default PDFUploadBox;

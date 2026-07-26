import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Info, HelpCircle } from 'lucide-react';
import PDFUploadBox from '../components/PDFUploadBox';
import { pdfAPI } from '../api';

const UploadPDF = () => {
  const navigate = useNavigate();

  const handleUploadSuccess = async (file) => {
    // Make the API call to upload the file to the backend
    await pdfAPI.upload(file);
  };

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '2.5rem 1.5rem',
      position: 'relative',
      zIndex: 10,
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem'
    }}>
      {/* Back button */}
      <div>
        <button 
          onClick={() => navigate('/dashboard')} 
          className="btn btn-secondary"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '6px 12px' }}
        >
          <ChevronLeft size={16} /> Back to Dashboard
        </button>
      </div>

      {/* Header */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '2.2rem', color: 'var(--text-navy)' }}>
          Upload Research Paper
        </h1>
        <p style={{ color: 'var(--text-navy-muted)', fontSize: '1.05rem', lineHeight: '1.5' }}>
          Upload your PDF. We'll parse the sections, formulas, and references, and build an AI index so you can start asking questions.
        </p>
      </div>

      {/* Upload Zone Component */}
      <PDFUploadBox onUploadSuccess={handleUploadSuccess} />

      {/* Info Tips */}
      <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', gap: '12px', alignItems: 'flex-start', background: 'rgba(255,255,255,0.6)' }}>
        <Info size={20} style={{ color: 'var(--accent-purple)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h4 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '0.95rem', marginBottom: '4px' }}>
            What happens after I upload?
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-navy-muted)', lineHeight: '1.4' }}>
            1. <strong>Text Extraction:</strong> We parse raw textual components using PyMuPDF.<br/>
            2. <strong>Vector Indexing:</strong> We segment the text into semantic chunks and generate embeddings using all-MiniLM-L6-v2, and build a local FAISS index.<br/>
            3. <strong>Ready to Chat:</strong> In the Chat tab, you can select your paper and get instant, simplified explanations backed by source references.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UploadPDF;

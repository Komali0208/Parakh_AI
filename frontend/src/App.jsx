import React, { useState } from 'react';
import Upload from './components/Upload';

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) return (
      <div style={{padding:'2rem',textAlign:'center',color:'#dc2626'}}>
        <p style={{fontWeight:600}}>Something went wrong.</p>
        <p style={{fontSize:'0.85rem',marginTop:'0.5rem'}}>{this.state.error?.message}</p>
        <button onClick={() => this.setState({hasError:false})}
          style={{marginTop:'1rem',padding:'0.5rem 1.5rem',background:'#c2410c',color:'#fff',border:'none',borderRadius:'6px',cursor:'pointer'}}>
          Try Again
        </button>
      </div>
    );
    return this.props.children;
  }
}

const styles = {
  page: { minHeight:'100vh', background:'#FAFAF7', fontFamily:"'Inter', sans-serif", color:'#1C1917' },
  header: { borderBottom:'1px solid #E7E5E4', padding:'1.5rem 2rem', display:'flex', alignItems:'center', justifyContent:'space-between', background:'#fff' },
  logo: { fontFamily:"'Playfair Display', serif", fontSize:'1.5rem', fontWeight:700, color:'#1C1917', letterSpacing:'-0.02em' },
  logoAccent: { color:'#C2410C' },
  tagline: { fontSize:'0.8rem', color:'#78716C', marginTop:'0.15rem' },
  badge: { background:'#FEF3C7', color:'#92400E', fontSize:'0.7rem', fontWeight:600, padding:'0.25rem 0.75rem', borderRadius:'999px', border:'1px solid #FDE68A', letterSpacing:'0.05em' },
  main: { maxWidth:'860px', margin:'0 auto', padding:'3rem 1.5rem' },
  heroTitle: { fontFamily:"'Playfair Display', serif", fontSize:'2.2rem', fontWeight:700, color:'#1C1917', lineHeight:1.2, marginBottom:'0.75rem' },
  heroSub: { fontSize:'1rem', color:'#78716C', lineHeight:1.7, maxWidth:'560px', marginBottom:'2.5rem' },
  card: { background:'#fff', border:'1px solid #E7E5E4', borderRadius:'12px', padding:'2rem', marginBottom:'1.5rem', boxShadow:'0 1px 4px rgba(0,0,0,0.04)' },
  tabs: { display:'flex', gap:'0', borderBottom:'1px solid #E7E5E4', marginBottom:'1.5rem' },
  tabActive: { padding:'0.6rem 1.25rem', fontSize:'0.9rem', fontWeight:600, color:'#C2410C', background:'none', border:'none', borderBottom:'2px solid #C2410C', cursor:'pointer' },
  tabInactive: { padding:'0.6rem 1.25rem', fontSize:'0.9rem', fontWeight:500, color:'#78716C', background:'none', border:'none', borderBottom:'2px solid transparent', cursor:'pointer' },
  textarea: { width:'100%', minHeight:'200px', padding:'1rem', border:'1px solid #E7E5E4', borderRadius:'8px', fontSize:'0.95rem', fontFamily:"'Inter', sans-serif", color:'#1C1917', background:'#FAFAF7', resize:'vertical', outline:'none', boxSizing:'border-box', lineHeight:1.7 },
  analyzeBtn: { marginTop:'1rem', padding:'0.65rem 1.75rem', background:'#C2410C', color:'#fff', border:'none', borderRadius:'8px', fontSize:'0.9rem', fontWeight:600, cursor:'pointer', letterSpacing:'0.01em' },
  errorText: { color:'#dc2626', fontSize:'0.85rem', marginTop:'0.5rem' },
  scoreCard: { background:'#fff', border:'1px solid #E7E5E4', borderRadius:'12px', padding:'1.5rem 2rem', marginBottom:'1.5rem', boxShadow:'0 1px 4px rgba(0,0,0,0.04)' },
  scoreTitle: { fontFamily:"'Playfair Display', serif", fontSize:'1.1rem', fontWeight:600, marginBottom:'0.75rem', color:'#1C1917' },
  progressTrack: { width:'100%', height:'10px', background:'#D1FAE5', borderRadius:'999px', overflow:'hidden', marginBottom:'1rem' },
  progressFill: (pct) => ({ height:'100%', width:`${pct}%`, background:'#DC2626', borderRadius:'999px', transition:'width 0.5s ease' }),
  legend: { display:'flex', gap:'1.5rem', fontSize:'0.8rem', color:'#78716C', alignItems:'center', marginBottom:'0.5rem' },
  legendDot: (color) => ({ width:'10px', height:'10px', borderRadius:'2px', background:color, display:'inline-block', marginRight:'5px' }),
  reportBtn: { padding:'0.55rem 1.25rem', background:'#fff', color:'#C2410C', border:'1px solid #C2410C', borderRadius:'8px', fontSize:'0.85rem', fontWeight:600, cursor:'pointer' },
  resultsTitle: { fontFamily:"'Playfair Display', serif", fontSize:'1.3rem', fontWeight:600, color:'#1C1917', marginBottom:'1rem' },
  inlineBox: { background:'#fff', border:'1px solid #E7E5E4', borderRadius:'12px', padding:'1.75rem 2rem', lineHeight:2, fontSize:'0.97rem', color:'#1C1917', boxShadow:'0 1px 4px rgba(0,0,0,0.04)' },
  footer: { borderTop:'1px solid #E7E5E4', padding:'1.5rem 2rem', textAlign:'center', fontSize:'0.78rem', color:'#A8A29E', background:'#fff' },
  spinner: { display:'flex', alignItems:'center', justifyContent:'center', gap:'0.75rem', padding:'2rem', color:'#78716C', fontSize:'0.9rem' },
};

export default function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [pasteText, setPasteText] = useState('');
  const [pasteError, setPasteError] = useState('');

  const handleResult = (data) => { setAnalysis(data); setLoading(false); };
  const handleStartUpload = () => { setLoading(true); setAnalysis(null); };

  const handleAnalyzePaste = async () => {
    if (!pasteText.trim()) { setPasteError('Please paste some text before analyzing.'); return; }
    setPasteError(''); setLoading(true); setAnalysis(null);
    try {
      const sentences = pasteText.replace(/([.?!])/g, "$1|").split("|").map(s => s.trim()).filter(s => s.length > 10);
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sentences }),
      });
      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      console.error(err); setAnalysis([]);
    } finally { setLoading(false); }
  };

  const handleDownloadReport = async () => {
    try {
      const response = await fetch('http://localhost:8000/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ results: analysis, filename: 'Parakh_Analysis' }),
      });
      if (!response.ok) throw new Error('Report generation failed');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'Parakh_Report.pdf'; a.click();
      URL.revokeObjectURL(url);
    } catch (err) { console.error(err); alert('Report generation failed. Check backend.'); }
  };

  const aiPercentage = Array.isArray(analysis) && analysis.length > 0
    ? ((analysis.filter(s => s.label === 'AI').length / analysis.length) * 100).toFixed(1)
    : 0;

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <div style={styles.logo}>Parakh<span style={styles.logoAccent}>.</span></div>
          <div style={styles.tagline}>AI Content Detection for Academic Integrity</div>
        </div>
        <span style={styles.badge}>BETA</span>
      </header>

      <main style={styles.main}>
        <h1 style={styles.heroTitle}>Is this written by a human?</h1>
        <p style={styles.heroSub}>Upload your assignment, research paper, or paste text directly. Parakh analyses every sentence and highlights AI-generated content — so you know exactly where to rewrite.</p>

        <div style={styles.card}>
          <div style={styles.tabs}>
            <button style={activeTab === 'upload' ? styles.tabActive : styles.tabInactive} onClick={() => setActiveTab('upload')}>Upload File</button>
            <button style={activeTab === 'paste' ? styles.tabActive : styles.tabInactive} onClick={() => setActiveTab('paste')}>Paste Text</button>
          </div>

          {activeTab === 'upload' && <Upload onResult={handleResult} onUploadStart={handleStartUpload} />}

          {activeTab === 'paste' && (
            <div>
              <textarea
                style={styles.textarea}
                placeholder="Paste your essay, assignment, or research paper here..."
                value={pasteText}
                onChange={e => setPasteText(e.target.value)}
              />
              {pasteError && <p style={styles.errorText}>{pasteError}</p>}
              <button style={styles.analyzeBtn} onClick={handleAnalyzePaste}>Analyse Text</button>
            </div>
          )}

          {loading && (
            <div style={styles.spinner}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C2410C" strokeWidth="2.5" strokeLinecap="round">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83">
                  <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                </path>
              </svg>
              Analysing your document...
            </div>
          )}
        </div>

        {Array.isArray(analysis) && analysis.length > 0 && (
          <ErrorBoundary>
            <div style={styles.scoreCard}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:'0.75rem'}}>
                <div>
                  <div style={styles.scoreTitle}>{aiPercentage}% of this document appears AI-generated</div>
                  <div style={styles.legend}>
                    <span><span style={styles.legendDot('rgba(220,38,38,0.4)')}></span>AI-generated</span>
                    <span><span style={styles.legendDot('rgba(34,197,94,0.35)')}></span>Human-written</span>
                    <span style={{color:'#A8A29E',fontSize:'0.75rem'}}>Hover any sentence for details</span>
                  </div>
                </div>
                <button style={styles.reportBtn} onClick={handleDownloadReport}>⬇ Download Report</button>
              </div>
              <div style={styles.progressTrack}>
                <div style={styles.progressFill(aiPercentage)}></div>
              </div>
            </div>

            <div style={styles.resultsTitle}>Analysis Results</div>
            <div style={styles.inlineBox}>
              {analysis.map((s, idx) => {
                const isAI = s.label === 'AI';
                return (
                  <span key={idx}
                    title={`${s.confidence}% ${s.label} — Keywords: ${s.keywords.join(', ')}`}
                    style={{
                      backgroundColor: isAI ? 'rgba(220,38,38,0.12)' : 'rgba(34,197,94,0.12)',
                      borderBottom: isAI ? '2px solid #DC2626' : '2px solid #16A34A',
                      borderRadius:'2px',
                      padding:'1px 0',
                      marginRight:'3px',
                      cursor:'default',
                    }}
                  >{s.sentence}{' '}</span>
                );
              })}
            </div>
          </ErrorBoundary>
        )}
      </main>

      <footer style={styles.footer}>
        <p>© {new Date().getFullYear()} Parakh AI — Built for academic integrity. Results are indicative, not conclusive.</p>
      </footer>
    </div>
  );
}

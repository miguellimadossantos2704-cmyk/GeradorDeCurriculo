import React, { useState } from 'react';
import ProfileDashboard from './components/ProfileDashboard';
import PDFUpload from './components/PDFUpload';
import JobSearch from './components/JobSearch';
import AutomationControl from './components/AutomationControl';

function App() {
    const [searchKeywords, setSearchKeywords] = useState('');
    const [cvUploaded, setCvUploaded] = useState(false);

    return (
        <div className="cyber-container">
            <header className="cyber-header">
                <h1>[ JOBHUNTER // AUTO-APPLY ]</h1>
            </header>

            <div className="dashboard-grid">
                <div className="left-column" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                    <ProfileDashboard />
                    <PDFUpload onUploadSuccess={() => setCvUploaded(true)} />
                    <JobSearch onSearchChange={setSearchKeywords} />
                </div>

                <div className="right-column">
                    <AutomationControl
                        keywords={searchKeywords}
                        isReady={cvUploaded}
                    />
                </div>
            </div>
        </div>
    );
}

export default App;

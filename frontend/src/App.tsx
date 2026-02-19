import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import InterviewSetup from './pages/InterviewSetup';
import InterviewRoom from './pages/InterviewRoom';
import Results from './pages/Results';
import Navbar from './components/Navbar';

function App() {
    const [studentId] = useState('00000000-0000-0000-0000-000000000001');

    return (
        <BrowserRouter>
            <div className="min-h-screen">
                <Navbar />
                <main className="container mx-auto px-4 py-8">
                    <Routes>
                        <Route path="/" element={<Dashboard studentId={studentId} />} />
                        <Route path="/upload" element={<ResumeUpload studentId={studentId} />} />
                        <Route path="/setup" element={<InterviewSetup studentId={studentId} />} />
                        <Route path="/interview/:sessionId" element={<InterviewRoom />} />
                        <Route path="/results/:sessionId" element={<Results />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}

export default App;

import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mic, Code, Users, Briefcase, Layers, ChevronRight, Loader2 } from 'lucide-react';
import axios from 'axios';

interface InterviewSetupProps {
    studentId: string;
}

function InterviewSetup({ studentId }: InterviewSetupProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const resumeId = location.state?.resumeId;

    const [interviewType, setInterviewType] = useState<string>('mixed');
    const [loading, setLoading] = useState(false);

    const interviewTypes = [
        { id: 'technical', label: 'Technical', icon: Code, description: 'Coding & system design questions' },
        { id: 'hr', label: 'HR/Behavioral', icon: Users, description: 'Behavioral & situational questions' },
        { id: 'mixed', label: 'Mixed', icon: Layers, description: 'Combination of all types' },
        { id: 'project_viva', label: 'Project Viva', icon: Briefcase, description: 'Based on your projects' },
    ];



    const startInterview = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/interview/create', {
                student_id: studentId,
                resume_id: resumeId,
                interview_type: interviewType
            });

            // Start the interview
            await axios.post(`/api/interview/${response.data.id}/start`);

            navigate(`/interview/${response.data.id}`);
        } catch (error) {
            console.error('Error creating interview:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-4"
            >
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl flex items-center justify-center">
                    <Mic className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-3xl font-bold">
                    Interview <span className="gradient-text">Setup</span>
                </h1>
                <p className="text-gray-400">
                    Customize your interview experience
                </p>
            </motion.div>

            {/* Interview Type Selection */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card"
            >
                <h3 className="text-lg font-semibold mb-4">Interview Type</h3>
                <div className="grid grid-cols-2 gap-4">
                    {interviewTypes.map((type) => {
                        const Icon = type.icon;
                        const isSelected = interviewType === type.id;
                        return (
                            <button
                                key={type.id}
                                onClick={() => setInterviewType(type.id)}
                                className={`p-4 rounded-xl border-2 text-left transition-all ${isSelected
                                    ? 'border-indigo-500 bg-indigo-500/10'
                                    : 'border-gray-700 hover:border-gray-600'
                                    }`}
                            >
                                <div className="flex items-start space-x-3">
                                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isSelected ? 'bg-indigo-500' : 'bg-dark-700'
                                        }`}>
                                        <Icon className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-gray-400'}`} />
                                    </div>
                                    <div>
                                        <p className={`font-medium ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                                            {type.label}
                                        </p>
                                        <p className="text-sm text-gray-500">{type.description}</p>
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </motion.div>



            {/* Interview Info */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="card bg-dark-800/50"
            >
                <h3 className="text-lg font-semibold mb-4">What to Expect</h3>
                <ul className="space-y-3 text-gray-400">
                    <li className="flex items-start space-x-3">
                        <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-indigo-400 text-sm">1</span>
                        </div>
                        <span>AI will ask you 10 personalized questions based on your profile</span>
                    </li>
                    <li className="flex items-start space-x-3">
                        <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-indigo-400 text-sm">2</span>
                        </div>
                        <span>Speak your answers naturally - the AI will transcribe and evaluate</span>
                    </li>
                    <li className="flex items-start space-x-3">
                        <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-indigo-400 text-sm">3</span>
                        </div>
                        <span>Get instant feedback and detailed performance analysis</span>
                    </li>
                </ul>
            </motion.div>

            {/* Start Button */}
            <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                onClick={startInterview}
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center space-x-2 py-4"
            >
                {loading ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Preparing Interview...</span>
                    </>
                ) : (
                    <>
                        <Mic className="w-5 h-5" />
                        <span>Start Interview</span>
                        <ChevronRight className="w-5 h-5" />
                    </>
                )}
            </motion.button>
        </div>
    );
}

export default InterviewSetup;

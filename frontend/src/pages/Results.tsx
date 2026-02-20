import { useState, useEffect } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    Award, TrendingUp, Target, AlertCircle, CheckCircle,
    Download, Share2, Home, RefreshCcw, ChevronRight
} from 'lucide-react';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';
import axios from 'axios';

function Results() {
    const { sessionId } = useParams();
    const location = useLocation();

    const [report, setReport] = useState<any>(location.state?.report || null);
    const [loading, setLoading] = useState(!location.state?.report);

    useEffect(() => {
        if (!report) {
            fetchReport();
        }
    }, [sessionId]);

    const fetchReport = async () => {
        try {
            const response = await axios.get(`/api/evaluation/${sessionId}/report`);
            setReport(response.data);
        } catch (error) {
            console.error('Error fetching report:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="mt-4 text-gray-400">Generating your report...</p>
                </div>
            </div>
        );
    }

    const overallScore = report?.performance?.overall_score || report?.overall_score || 0;
    const grade = report?.performance?.grade || report?.grade || 'F';

    const scoreData = [{
        name: 'Score',
        value: overallScore,
        fill: overallScore >= 70 ? '#10b981' : overallScore >= 50 ? '#f59e0b' : '#ef4444'
    }];

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-4"
            >
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-green-500 to-emerald-600 rounded-3xl flex items-center justify-center">
                    <Award className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-3xl font-bold">
                    Interview <span className="gradient-text">Complete!</span>
                </h1>
                <p className="text-gray-400">
                    Here's your detailed performance analysis
                </p>
            </motion.div>

            {/* Score Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card bg-gradient-to-br from-dark-800 to-dark-900"
            >
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Overall Score */}
                    <div className="flex flex-col items-center justify-center">
                        <div className="relative w-48 h-48">
                            <ResponsiveContainer>
                                <RadialBarChart
                                    cx="50%"
                                    cy="50%"
                                    innerRadius="70%"
                                    outerRadius="100%"
                                    data={scoreData}
                                    startAngle={90}
                                    endAngle={-270}
                                >
                                    <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                                    <RadialBar dataKey="value" cornerRadius={10} background={{ fill: '#1e293b' }} />
                                </RadialBarChart>
                            </ResponsiveContainer>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-5xl font-bold">{Math.round(overallScore)}</span>
                                <span className="text-gray-400">out of 100</span>
                            </div>
                        </div>
                        <div className="mt-4 text-center">
                            <span className={`text-3xl font-bold ${grade.startsWith('A') ? 'text-green-400' :
                                grade.startsWith('B') ? 'text-blue-400' :
                                    grade.startsWith('C') ? 'text-amber-400' : 'text-red-400'
                                }`}>
                                Grade: {grade}
                            </span>
                        </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="lg:col-span-2 space-y-4">
                        <h3 className="text-lg font-semibold mb-4">Score Breakdown</h3>
                        {[
                            { label: 'Technical Accuracy', value: report?.category_scores?.technical || 0, color: 'bg-indigo-500' },
                            { label: 'Communication', value: report?.category_scores?.hr || 0, color: 'bg-blue-500' },
                            { label: 'Problem Solving', value: report?.category_scores?.scenario || 0, color: 'bg-purple-500' },
                            { label: 'Domain Knowledge', value: report?.category_scores?.project || 0, color: 'bg-pink-500' },
                        ].map((item, index) => (
                            <div key={index} className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">{item.label}</span>
                                    <span>{Math.round(item.value)}%</span>
                                </div>
                                <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${item.value}%` }}
                                        transition={{ delay: 0.3 + index * 0.1 }}
                                        className={`h-full ${item.color} rounded-full`}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </motion.div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="card"
                >
                    <div className="flex items-center space-x-2 mb-4">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <h3 className="text-lg font-semibold">Strengths</h3>
                    </div>
                    <ul className="space-y-3">
                        {(report?.strengths || ['Participated in the interview']).map((strength: string, i: number) => (
                            <li key={i} className="flex items-start space-x-3">
                                <TrendingUp className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                                <span className="text-gray-300">{strength}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="card"
                >
                    <div className="flex items-center space-x-2 mb-4">
                        <AlertCircle className="w-5 h-5 text-amber-400" />
                        <h3 className="text-lg font-semibold">Areas to Improve</h3>
                    </div>
                    <ul className="space-y-3">
                        {(report?.weaknesses || ['No data available']).map((weakness: string, i: number) => (
                            <li key={i} className="flex items-start space-x-3">
                                <Target className="w-4 h-4 text-amber-400 mt-1 flex-shrink-0" />
                                <span className="text-gray-300">{weakness}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>
            </div>

            {/* Improvement Suggestions */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="card"
            >
                <h3 className="text-lg font-semibold mb-4">Improvement Suggestions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {(report?.improvement_suggestions || [
                        'Practice answering questions out loud',
                        'Review core technical concepts',
                        'Prepare STAR method responses'
                    ]).map((suggestion: string, i: number) => (
                        <div key={i} className="p-4 rounded-xl bg-dark-800/50 flex items-start space-x-3">
                            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
                                <span className="text-indigo-400 text-sm">{i + 1}</span>
                            </div>
                            <span className="text-gray-300">{suggestion}</span>
                        </div>
                    ))}
                </div>
            </motion.div>

            {/* Placement Status */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className={`card ${report?.performance?.placement_ready === 'Ready' || report?.placement_ready === 'Ready'
                    ? 'bg-green-500/10 border-green-500/30'
                    : 'bg-amber-500/10 border-amber-500/30'
                    }`}
            >
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-semibold">Placement Readiness</h3>
                        <p className="text-gray-400 mt-1">Based on your interview performance</p>
                    </div>
                    <span className={`text-2xl font-bold ${report?.performance?.placement_ready === 'Ready' || report?.placement_ready === 'Ready'
                        ? 'text-green-400'
                        : 'text-amber-400'
                        }`}>
                        {report?.performance?.placement_ready || report?.placement_ready || 'In Progress'}
                    </span>
                </div>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="flex flex-wrap justify-center gap-4"
            >
                <Link to="/" className="btn-secondary flex items-center space-x-2">
                    <Home className="w-4 h-4" />
                    <span>Back to Dashboard</span>
                </Link>
                <Link to="/setup" className="btn-primary flex items-center space-x-2">
                    <RefreshCcw className="w-4 h-4" />
                    <span>Take Another Interview</span>
                </Link>
                <button className="btn-secondary flex items-center space-x-2">
                    <Download className="w-4 h-4" />
                    <span>Download Report</span>
                </button>
            </motion.div>
        </div>
    );
}

export default Results;

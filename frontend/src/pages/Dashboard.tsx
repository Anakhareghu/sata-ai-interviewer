import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    Mic, FileText, TrendingUp, Award, Clock,
    ChevronRight, BarChart2, Target, Sparkles
} from 'lucide-react';
import axios from 'axios';

interface DashboardProps {
    studentId: string;
}

function Dashboard({ studentId }: DashboardProps) {
    const [stats, setStats] = useState({
        totalInterviews: 0,
        averageScore: 0,
        resumesUploaded: 0,
        lastInterview: null as string | null,
    });
    const [recentInterviews, setRecentInterviews] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, [studentId]);

    const fetchDashboardData = async () => {
        try {
            // Fetch interview history
            const response = await axios.get(`/api/interview/student/${studentId}/history`);
            const interviews = response.data.interviews || [];

            setRecentInterviews(interviews.slice(0, 5));
            setStats({
                totalInterviews: interviews.length,
                averageScore: 75, // Would calculate from actual data
                resumesUploaded: 1, // Would fetch from API
                lastInterview: interviews[0]?.created_at || null,
            });
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const statCards = [
        {
            label: 'Total Interviews',
            value: stats.totalInterviews,
            icon: Mic,
            color: 'from-indigo-500 to-purple-500',
            bgColor: 'bg-indigo-500/10'
        },
        {
            label: 'Average Score',
            value: `${stats.averageScore}%`,
            icon: TrendingUp,
            color: 'from-green-500 to-emerald-500',
            bgColor: 'bg-green-500/10'
        },
        {
            label: 'Resumes Uploaded',
            value: stats.resumesUploaded,
            icon: FileText,
            color: 'from-blue-500 to-cyan-500',
            bgColor: 'bg-blue-500/10'
        },
        {
            label: 'Placement Ready',
            value: stats.averageScore >= 70 ? 'Yes' : 'In Progress',
            icon: Award,
            color: 'from-amber-500 to-orange-500',
            bgColor: 'bg-amber-500/10'
        },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-4"
            >
                <h1 className="text-4xl font-bold">
                    Welcome to <span className="gradient-text">AI Voice Interview</span>
                </h1>
                <p className="text-gray-400 max-w-2xl mx-auto">
                    Practice your interview skills with our AI-powered voice interview system.
                    Upload your resume, take mock interviews, and get instant feedback.
                </p>
            </motion.div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((stat, index) => {
                    const Icon = stat.icon;
                    return (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="card"
                        >
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-gray-400 text-sm">{stat.label}</p>
                                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                                </div>
                                <div className={`w-12 h-12 rounded-xl ${stat.bgColor} flex items-center justify-center`}>
                                    <Icon className={`w-6 h-6 bg-gradient-to-r ${stat.color} bg-clip-text`}
                                        style={{ color: stat.color.includes('indigo') ? '#6366f1' : stat.color.includes('green') ? '#10b981' : stat.color.includes('blue') ? '#3b82f6' : '#f59e0b' }} />
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>

            {/* Action Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Start Interview Card */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="card bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border-indigo-500/30"
                >
                    <div className="flex items-start justify-between">
                        <div className="space-y-4">
                            <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center">
                                <Mic className="w-7 h-7 text-white" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold">Start AI Interview</h3>
                                <p className="text-gray-400 mt-1">
                                    Practice with our AI interviewer and get instant feedback
                                </p>
                            </div>
                            <Link
                                to="/setup"
                                className="btn-primary inline-flex items-center space-x-2"
                            >
                                <span>Start Now</span>
                                <ChevronRight className="w-4 h-4" />
                            </Link>
                        </div>
                        <Sparkles className="w-24 h-24 text-indigo-500/20" />
                    </div>
                </motion.div>

                {/* Upload Resume Card */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="card bg-gradient-to-br from-blue-600/20 to-cyan-600/20 border-blue-500/30"
                >
                    <div className="flex items-start justify-between">
                        <div className="space-y-4">
                            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center">
                                <FileText className="w-7 h-7 text-white" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold">Upload Resume</h3>
                                <p className="text-gray-400 mt-1">
                                    Get personalized questions based on your skills and experience
                                </p>
                            </div>
                            <Link
                                to="/upload"
                                className="btn-secondary inline-flex items-center space-x-2"
                            >
                                <span>Upload CV</span>
                                <ChevronRight className="w-4 h-4" />
                            </Link>
                        </div>
                        <Target className="w-24 h-24 text-blue-500/20" />
                    </div>
                </motion.div>
            </div>

            {/* Recent Interviews */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="card"
            >
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold">Recent Interviews</h3>
                    <BarChart2 className="w-5 h-5 text-gray-400" />
                </div>

                {recentInterviews.length > 0 ? (
                    <div className="space-y-4">
                        {recentInterviews.map((interview, index) => (
                            <Link
                                key={interview.id}
                                to={`/results/${interview.id}`}
                                className="flex items-center justify-between p-4 rounded-xl bg-dark-800/50 hover:bg-dark-700/50 transition-all"
                            >
                                <div className="flex items-center space-x-4">
                                    <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                                        <Mic className="w-5 h-5 text-indigo-400" />
                                    </div>
                                    <div>
                                        <p className="font-medium">{interview.interview_type} Interview</p>
                                        <p className="text-sm text-gray-400">
                                            {new Date(interview.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-4">
                                    <span className={`px-3 py-1 rounded-full text-sm ${interview.status === 'completed'
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-amber-500/20 text-amber-400'
                                        }`}>
                                        {interview.status}
                                    </span>
                                    <ChevronRight className="w-5 h-5 text-gray-400" />
                                </div>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                        <p className="text-gray-400">No interviews yet</p>
                        <p className="text-sm text-gray-500 mt-1">Start your first AI interview to see results here</p>
                    </div>
                )}
            </motion.div>
        </div>
    );
}

export default Dashboard;

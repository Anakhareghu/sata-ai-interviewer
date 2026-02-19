import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react';
import axios from 'axios';

interface ResumeUploadProps {
    studentId: string;
}

function ResumeUpload({ studentId }: ResumeUploadProps) {
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [parsedData, setParsedData] = useState<any>(null);
    const [error, setError] = useState<string>('');
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (selectedFile: File) => {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!validTypes.includes(selectedFile.type)) {
            setError('Please upload a PDF or DOCX file');
            return;
        }
        if (selectedFile.size > 10 * 1024 * 1024) {
            setError('File size must be less than 10MB');
            return;
        }
        setFile(selectedFile);
        setError('');
        setUploadStatus('idle');
    };

    const uploadResume = async () => {
        if (!file) return;

        setUploading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('student_id', studentId);

        try {
            const response = await axios.post('/api/resume/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // Fetch the parsed resume data
            const resumeData = await axios.get(`/api/resume/${response.data.id}`);
            setParsedData(resumeData.data);
            setUploadStatus('success');

        } catch (err: any) {
            setError(err.response?.data?.detail || 'Upload failed');
            setUploadStatus('error');
        } finally {
            setUploading(false);
        }
    };

    const startInterview = () => {
        navigate('/setup', { state: { resumeId: parsedData?.id } });
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-4"
            >
                <h1 className="text-3xl font-bold">
                    Upload Your <span className="gradient-text">Resume</span>
                </h1>
                <p className="text-gray-400">
                    We'll analyze your resume to generate personalized interview questions
                </p>
            </motion.div>

            {/* Upload Area */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card"
            >
                <div
                    className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${dragActive
                            ? 'border-indigo-500 bg-indigo-500/10'
                            : 'border-gray-600 hover:border-gray-500'
                        }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.docx"
                        onChange={handleFileInput}
                        className="hidden"
                    />

                    {file ? (
                        <div className="space-y-4">
                            <div className="w-16 h-16 mx-auto bg-indigo-500/20 rounded-2xl flex items-center justify-center">
                                <FileText className="w-8 h-8 text-indigo-400" />
                            </div>
                            <div>
                                <p className="font-medium">{file.name}</p>
                                <p className="text-sm text-gray-400">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                            <button
                                onClick={() => setFile(null)}
                                className="text-red-400 hover:text-red-300 text-sm flex items-center justify-center space-x-1 mx-auto"
                            >
                                <X className="w-4 h-4" />
                                <span>Remove</span>
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div className="w-16 h-16 mx-auto bg-dark-700 rounded-2xl flex items-center justify-center">
                                <Upload className="w-8 h-8 text-gray-400" />
                            </div>
                            <div>
                                <p className="text-lg font-medium">
                                    Drag and drop your resume here
                                </p>
                                <p className="text-gray-400 text-sm mt-1">
                                    or{' '}
                                    <button
                                        onClick={() => fileInputRef.current?.click()}
                                        className="text-indigo-400 hover:text-indigo-300"
                                    >
                                        browse files
                                    </button>
                                </p>
                            </div>
                            <p className="text-xs text-gray-500">
                                Supports PDF and DOCX up to 10MB
                            </p>
                        </div>
                    )}
                </div>

                {error && (
                    <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center space-x-2">
                        <AlertCircle className="w-5 h-5 text-red-400" />
                        <span className="text-red-400">{error}</span>
                    </div>
                )}

                {file && uploadStatus !== 'success' && (
                    <button
                        onClick={uploadResume}
                        disabled={uploading}
                        className="btn-primary w-full mt-6 flex items-center justify-center space-x-2"
                    >
                        {uploading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Analyzing Resume...</span>
                            </>
                        ) : (
                            <>
                                <Upload className="w-5 h-5" />
                                <span>Upload & Analyze</span>
                            </>
                        )}
                    </button>
                )}
            </motion.div>

            {/* Parsed Data Display */}
            {uploadStatus === 'success' && parsedData && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                >
                    <div className="card bg-green-500/10 border-green-500/30">
                        <div className="flex items-center space-x-3">
                            <CheckCircle className="w-6 h-6 text-green-400" />
                            <span className="font-medium text-green-400">Resume analyzed successfully!</span>
                        </div>
                    </div>

                    {/* Skills */}
                    <div className="card">
                        <h3 className="text-lg font-semibold mb-4">Extracted Skills</h3>
                        <div className="space-y-4">
                            <div>
                                <p className="text-sm text-gray-400 mb-2">Technical Skills</p>
                                <div className="flex flex-wrap gap-2">
                                    {parsedData.extracted_skills?.technical?.map((skill: string, i: number) => (
                                        <span key={i} className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-sm">
                                            {skill}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <p className="text-sm text-gray-400 mb-2">Soft Skills</p>
                                <div className="flex flex-wrap gap-2">
                                    {parsedData.extracted_skills?.soft?.map((skill: string, i: number) => (
                                        <span key={i} className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-sm">
                                            {skill}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Domain & Level */}
                    <div className="grid grid-cols-2 gap-6">
                        <div className="card">
                            <p className="text-sm text-gray-400">Domain Specialization</p>
                            <p className="text-xl font-semibold mt-1">{parsedData.domain_specialization || 'General'}</p>
                        </div>
                        <div className="card">
                            <p className="text-sm text-gray-400">Experience Level</p>
                            <p className="text-xl font-semibold mt-1">{parsedData.experience_level || 'Entry Level'}</p>
                        </div>
                    </div>

                    {/* Start Interview Button */}
                    <button
                        onClick={startInterview}
                        className="btn-primary w-full flex items-center justify-center space-x-2"
                    >
                        <span>Continue to Interview Setup</span>
                    </button>
                </motion.div>
            )}
        </div>
    );
}

export default ResumeUpload;

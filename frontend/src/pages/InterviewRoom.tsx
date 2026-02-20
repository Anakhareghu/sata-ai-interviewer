import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mic, MicOff, SkipForward, StopCircle, Volume2, Loader2 } from 'lucide-react';

// Check for Web Speech API support
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

function InterviewRoom() {
    const { sessionId } = useParams();
    const navigate = useNavigate();

    const [currentQuestion, setCurrentQuestion] = useState<any>(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isAISpeaking, setIsAISpeaking] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [questionNumber, setQuestionNumber] = useState(1);
    const [totalQuestions, setTotalQuestions] = useState(10);
    const [feedback, setFeedback] = useState<string | null>(null);
    const [questions, setQuestions] = useState<any[]>([]);
    const [responses, setResponses] = useState<any[]>([]);
    const [questionScores, setQuestionScores] = useState<{ idx: number, score: number, skipped: boolean }[]>([]);

    const recognitionRef = useRef<any>(null);
    const synthRef = useRef(window.speechSynthesis);

    useEffect(() => {
        initializeInterview();
        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
            synthRef.current.cancel();
        };
    }, [sessionId]);

    const initializeInterview = async () => {
        try {
            // Fetch questions from API
            const response = await fetch(`/api/interview/${sessionId}/questions`);
            if (response.ok) {
                const data = await response.json();
                setQuestions(data.questions || []);
                setTotalQuestions(data.questions?.length || 10);
                if (data.questions?.length > 0) {
                    askQuestion(data.questions[0], 1);
                }
            } else {
                // Use mock questions for demo
                const mockQuestions = [
                    { question_text: "Tell me about yourself and your background in technology.", question_type: "hr" },
                    { question_text: "What programming languages are you most proficient in?", question_type: "technical" },
                    { question_text: "Describe a challenging project you've worked on.", question_type: "project" },
                    { question_text: "How do you handle debugging a complex issue?", question_type: "scenario" },
                    { question_text: "What are your career goals for the next 5 years?", question_type: "hr" },
                ];
                setQuestions(mockQuestions);
                setTotalQuestions(mockQuestions.length);
                askQuestion(mockQuestions[0], 1);
            }
        } catch (error) {
            console.error('Error fetching questions:', error);
        }
    };

    const askQuestion = (question: any, number: number) => {
        setCurrentQuestion(question);
        setQuestionNumber(number);
        setTranscript('');
        setFeedback(null);

        // Use Text-to-Speech to speak the question
        speakText(question.question_text);
    };

    const speakText = (text: string) => {
        setIsAISpeaking(true);
        synthRef.current.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;

        utterance.onend = () => {
            setIsAISpeaking(false);
        };

        utterance.onerror = () => {
            setIsAISpeaking(false);
        };

        synthRef.current.speak(utterance);
    };

    const startRecording = () => {
        if (!SpeechRecognition) {
            alert('Speech recognition is not supported in this browser. Please use Chrome.');
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event: any) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            setTranscript(prev => prev + finalTranscript || interimTranscript);
        };

        recognition.onerror = (event: any) => {
            console.error('Speech recognition error:', event.error);
            setIsRecording(false);
        };

        recognition.onend = () => {
            if (isRecording) {
                // Restart if still recording
                recognition.start();
            }
        };

        recognitionRef.current = recognition;
        recognition.start();
        setIsRecording(true);
        setTranscript('');
    };

    const evaluateAnswer = (answer: string, question: any): number => {
        if (!answer || answer.trim().length < 5) return 0;

        const wordCount = answer.split(' ').length;
        const answerLower = answer.toLowerCase();

        // Keyword match score (0-10)
        const expectedKeywords: string[] = question?.expected_keywords || [];
        let keywordScore = 5; // default if no keywords
        if (expectedKeywords.length > 0) {
            const matches = expectedKeywords.filter(kw => answerLower.includes(kw.toLowerCase())).length;
            keywordScore = (matches / expectedKeywords.length) * 10;
        }

        // Length/detail score (0-10)
        let lengthScore = Math.min(10, wordCount / 10);

        // Structure score (0-10)
        let structureScore = 4;
        if (['for example', 'such as', 'because', 'therefore'].some(w => answerLower.includes(w))) structureScore += 2;
        if (['first', 'second', 'third', 'step'].some(w => answerLower.includes(w))) structureScore += 2;
        if (wordCount >= 30) structureScore += 2;

        // Weighted final score (0-10)
        const finalScore = Math.round(Math.max(1, Math.min(10, keywordScore * 0.4 + lengthScore * 0.3 + structureScore * 0.3)) * 10) / 10;
        return finalScore;
    };

    const stopRecording = async () => {
        setIsRecording(false);
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }

        if (!transcript.trim()) {
            setFeedback('No response detected. Please try again.');
            return;
        }

        setIsProcessing(true);

        // Store the response
        const response = {
            question_idx: questionNumber - 1,
            response_text: transcript,
            timestamp: new Date().toISOString()
        };
        setResponses(prev => [...prev, response]);

        // Score based on answer quality and keyword matching
        const score = evaluateAnswer(transcript, currentQuestion);
        setQuestionScores(prev => [...prev, { idx: questionNumber - 1, score, skipped: false }]);

        if (score < 4) {
            setFeedback(`Score: ${score}/10 — Try to provide more detailed responses with specific examples.`);
        } else if (score < 7) {
            setFeedback(`Score: ${score}/10 — Good start! Consider adding more depth and examples.`);
        } else {
            setFeedback(`Score: ${score}/10 — Great response!`);
        }

        setIsProcessing(false);

        // Wait a moment before next question
        setTimeout(() => {
            moveToNextQuestion();
        }, 2000);
    };

    const moveToNextQuestion = () => {
        const nextNumber = questionNumber + 1;
        if (nextNumber <= questions.length) {
            askQuestion(questions[nextNumber - 1], nextNumber);
        } else {
            endInterview();
        }
    };

    const skipQuestion = () => {
        // Record skipped question with 0 score
        setQuestionScores(prev => [...prev, { idx: questionNumber - 1, score: 0, skipped: true }]);
        setFeedback('Question skipped — scored as 0.');
        setTimeout(() => {
            moveToNextQuestion();
        }, 1000);
    };

    const endInterview = () => {
        // Calculate actual scores from all questions (including skipped as 0)
        const allScores = [...questionScores];

        // Any questions not answered or skipped also count as 0
        for (let i = 0; i < questions.length; i++) {
            if (!allScores.find(s => s.idx === i)) {
                allScores.push({ idx: i, score: 0, skipped: true });
            }
        }

        const totalQuestions = questions.length;
        const answeredCount = allScores.filter(s => !s.skipped).length;
        const skippedCount = allScores.filter(s => s.skipped).length;

        // Overall score out of 100 — average of ALL questions (skipped = 0)
        const avgScore = totalQuestions > 0
            ? allScores.reduce((sum, s) => sum + s.score, 0) / totalQuestions
            : 0;
        const overallScore = Math.round(avgScore * 10); // Convert 0-10 to 0-100

        // Category scores
        const categoryScores: Record<string, number[]> = {};
        allScores.forEach(s => {
            const q = questions[s.idx];
            const qType = q?.question_type || 'general';
            if (!categoryScores[qType]) categoryScores[qType] = [];
            categoryScores[qType].push(s.score);
        });

        const catAvg: Record<string, number> = {};
        Object.entries(categoryScores).forEach(([type, scores]) => {
            catAvg[type] = Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10);
        });

        // Grade calculation
        let grade = 'F';
        if (overallScore >= 90) grade = 'A+';
        else if (overallScore >= 80) grade = 'A';
        else if (overallScore >= 70) grade = 'B+';
        else if (overallScore >= 60) grade = 'B';
        else if (overallScore >= 50) grade = 'C+';
        else if (overallScore >= 40) grade = 'C';
        else if (overallScore >= 30) grade = 'D';

        // Strengths & weaknesses
        const strengths: string[] = [];
        const weaknesses: string[] = [];

        Object.entries(catAvg).forEach(([type, avg]) => {
            if (avg >= 70) strengths.push(`Strong ${type} skills`);
            else if (avg < 40) weaknesses.push(`Needs improvement in ${type} areas`);
        });

        if (skippedCount > 0) weaknesses.push(`Skipped ${skippedCount} question(s)`);
        if (answeredCount === totalQuestions && overallScore >= 60) strengths.push('Answered all questions');
        if (strengths.length === 0) strengths.push('Participated in the interview');
        if (weaknesses.length === 0) weaknesses.push('No major weaknesses identified');

        // Suggestions
        const suggestions: string[] = [];
        if (overallScore < 70) suggestions.push('Practice answering questions out loud to improve fluency');
        if (catAvg['technical'] !== undefined && catAvg['technical'] < 60) suggestions.push('Review core technical concepts and practice coding problems');
        if (catAvg['hr'] !== undefined && catAvg['hr'] < 60) suggestions.push('Prepare STAR method responses for behavioral questions');
        if (skippedCount > 0) suggestions.push('Try to attempt all questions instead of skipping');
        if (overallScore < 50) suggestions.push('Consider taking mock interviews to build confidence');
        if (suggestions.length === 0) suggestions.push('Continue practicing to maintain your skills');

        const placementReady = overallScore >= 70 ? 'Ready' : overallScore >= 50 ? 'Needs Work' : 'Not Ready';

        const report = {
            overall_score: overallScore,
            grade,
            questions_answered: answeredCount,
            total_questions: totalQuestions,
            questions_skipped: skippedCount,
            category_scores: catAvg,
            strengths,
            weaknesses,
            improvement_suggestions: suggestions,
            placement_ready: placementReady
        };

        navigate(`/results/${sessionId}`, { state: { report } });
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Progress Bar */}
            <div className="card">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Question {questionNumber} of {totalQuestions}</span>
                    <span className="text-sm text-gray-400">{Math.round((questionNumber / totalQuestions) * 100)}%</span>
                </div>
                <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                    />
                </div>
            </div>

            {/* Main Interview Area */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="card min-h-[400px] flex flex-col"
            >
                {/* AI Avatar & Status */}
                <div className="flex items-center space-x-4 mb-6">
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center ${isAISpeaking ? 'recording-pulse' : ''}`}>
                        <Volume2 className={`w-8 h-8 text-white ${isAISpeaking ? 'animate-pulse' : ''}`} />
                    </div>
                    <div>
                        <h3 className="font-semibold">AI Interviewer</h3>
                        <p className="text-sm text-gray-400">
                            {isAISpeaking ? 'Speaking...' : isRecording ? 'Listening...' : 'Ready'}
                        </p>
                    </div>
                </div>

                {/* Question Display */}
                <div className="flex-1 space-y-6">
                    {currentQuestion ? (
                        <div className="p-6 rounded-xl bg-dark-800/50">
                            <span className="text-xs text-indigo-400 uppercase tracking-wide">
                                {currentQuestion.question_type} Question
                            </span>
                            <p className="text-xl mt-2">{currentQuestion.question_text}</p>
                        </div>
                    ) : (
                        <div className="flex items-center justify-center h-40">
                            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                        </div>
                    )}

                    {/* Transcript */}
                    {transcript && (
                        <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/30">
                            <p className="text-sm text-gray-400 mb-1">Your Response:</p>
                            <p>{transcript}</p>
                        </div>
                    )}

                    {/* Feedback */}
                    {feedback && (
                        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
                            <p className="text-sm text-amber-400">{feedback}</p>
                        </div>
                    )}
                </div>

                {/* Recording Controls */}
                <div className="flex items-center justify-center space-x-4 mt-8">
                    {isProcessing ? (
                        <div className="flex items-center space-x-2 text-gray-400">
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Processing...</span>
                        </div>
                    ) : (
                        <>
                            <button
                                onClick={isRecording ? stopRecording : startRecording}
                                disabled={isAISpeaking}
                                className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${isRecording
                                    ? 'bg-red-500 recording-pulse'
                                    : 'bg-gradient-to-br from-indigo-500 to-purple-600 hover:opacity-90'
                                    } ${isAISpeaking ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {isRecording ? (
                                    <MicOff className="w-8 h-8 text-white" />
                                ) : (
                                    <Mic className="w-8 h-8 text-white" />
                                )}
                            </button>

                            {/* Audio Visualizer */}
                            {isRecording && (
                                <div className="flex items-center space-x-1 h-8">
                                    {[...Array(5)].map((_, i) => (
                                        <div
                                            key={i}
                                            className="audio-bar"
                                            style={{ animationDelay: `${i * 0.1}s` }}
                                        />
                                    ))}
                                </div>
                            )}
                        </>
                    )}
                </div>

                <p className="text-center text-sm text-gray-400 mt-4">
                    {isRecording ? 'Click to stop recording' : 'Click the microphone to start speaking'}
                </p>

                {!SpeechRecognition && (
                    <p className="text-center text-sm text-red-400 mt-2">
                        ⚠️ Speech recognition not supported. Please use Chrome or Edge browser.
                    </p>
                )}
            </motion.div>

            {/* Action Buttons */}
            <div className="flex justify-between">
                <button
                    onClick={skipQuestion}
                    className="btn-secondary flex items-center space-x-2"
                >
                    <SkipForward className="w-4 h-4" />
                    <span>Skip Question</span>
                </button>

                <button
                    onClick={endInterview}
                    className="bg-red-500/20 text-red-400 px-6 py-3 rounded-xl font-semibold hover:bg-red-500/30 transition-all flex items-center space-x-2"
                >
                    <StopCircle className="w-4 h-4" />
                    <span>End Interview</span>
                </button>
            </div>
        </div>
    );
}

export default InterviewRoom;

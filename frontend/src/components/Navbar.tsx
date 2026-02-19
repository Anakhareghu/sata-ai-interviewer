import { Link, useLocation } from 'react-router-dom';
import { Mic, FileText, LayoutDashboard, Settings } from 'lucide-react';

function Navbar() {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/upload', label: 'Upload Resume', icon: FileText },
        { path: '/setup', label: 'Start Interview', icon: Mic },
    ];

    return (
        <nav className="glass border-b border-white/10">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                            <Mic className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold gradient-text">AI Interview</span>
                    </Link>

                    {/* Navigation */}
                    <div className="flex items-center space-x-2">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${isActive
                                            ? 'bg-indigo-600/20 text-indigo-400'
                                            : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    <Icon className="w-4 h-4" />
                                    <span className="text-sm font-medium">{item.label}</span>
                                </Link>
                            );
                        })}
                    </div>

                    {/* Settings */}
                    <button className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-all">
                        <Settings className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;

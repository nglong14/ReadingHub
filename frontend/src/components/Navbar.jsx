import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AuthModal from './AuthModal';
import './Navbar.css';

function Navbar() {
    const { user, signOut, loading } = useAuth();
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

    const handleSignOut = async () => {
        try {
            await signOut();
        } catch (error) {
            console.error('Error signing out:', error);
        }
    };

    const openAuthModal = () => {
        setIsAuthModalOpen(true);
    };

    const closeAuthModal = () => {
        setIsAuthModalOpen(false);
    };

    return (
        <>
            <nav className="navbar">
                <div className="navbar-container">
                    <div className="navbar-brand">
                        <span className="navbar-icon">📚</span>
                        <h1 className="navbar-title">Book Recommendation</h1>
                    </div>

                    <div className="navbar-actions">
                        {loading ? (
                            <div className="navbar-loading">
                                <span className="loading-spinner">⏳</span>
                            </div>
                        ) : user ? (
                            <>
                                <span className="navbar-user">
                                    <span className="user-icon">👤</span>
                                    {user.email}
                                </span>
                                <button className="navbar-btn logout-btn" onClick={handleSignOut}>
                                    Log Out
                                </button>
                            </>
                        ) : (
                            <button className="navbar-btn signin-btn" onClick={openAuthModal}>
                                Sign In
                            </button>
                        )}
                    </div>
                </div>
            </nav>

            <AuthModal isOpen={isAuthModalOpen} onClose={closeAuthModal} />
        </>
    );
}

export default Navbar;


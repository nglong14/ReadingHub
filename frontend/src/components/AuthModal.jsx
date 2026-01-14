import { useState } from 'react';
import SignIn from './SignIn';
import SignUp from './SignUp';
import './AuthModal.css';

function AuthModal({ isOpen, onClose }) {
    const [isSignIn, setIsSignIn] = useState(true);

    if (!isOpen) return null;

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    const handleSwitchToSignUp = () => {
        setIsSignIn(false);
    };

    const handleSwitchToSignIn = () => {
        setIsSignIn(true);
    };

    return (
        <div className="auth-modal-backdrop" onClick={handleBackdropClick}>
            <div className="auth-modal">
                <button className="auth-modal-close" onClick={onClose} aria-label="Close">
                    ✕
                </button>
                {isSignIn ? (
                    <SignIn onSwitchToSignUp={handleSwitchToSignUp} onClose={onClose} />
                ) : (
                    <SignUp onSwitchToSignIn={handleSwitchToSignIn} onClose={onClose} />
                )}
            </div>
        </div>
    );
}

export default AuthModal;

import { useState } from 'react';
import './Navbar.css';

function Navbar() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [username, setUsername] = useState('');

    const handleSignIn = () => {
        // Placeholder for sign-in logic
        const name = prompt('Enter your username:');
        if (name) {
            setUsername(name);
            setIsLoggedIn(true);
        }
    };

    const handleLogOut = () => {
        setIsLoggedIn(false);
        setUsername('');
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-brand">
                    <span className="navbar-icon">📚</span>
                    <h1 className="navbar-title">Book Recommendation</h1>
                </div>

                <div className="navbar-actions">
                    {isLoggedIn ? (
                        <>
                            <span className="navbar-user">
                                <span className="user-icon">👤</span>
                                {username}
                            </span>
                            <button className="navbar-btn logout-btn" onClick={handleLogOut}>
                                Log Out
                            </button>
                        </>
                    ) : (
                        <button className="navbar-btn signin-btn" onClick={handleSignIn}>
                            Sign In
                        </button>
                    )}
                </div>
            </div>
        </nav>
    );
}

export default Navbar;

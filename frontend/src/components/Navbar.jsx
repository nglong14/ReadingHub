import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

function Navbar() {
    const { user, signOut, loading } = useAuth();

    const handleSignOut = async () => {
        try {
            await signOut();
        } catch (error) {
            console.error('Error signing out:', error);
        }
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-brand">
                    <span className="navbar-icon">📚</span>
                    <h1 className="navbar-title">Book Recommendation</h1>
                </Link>

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
                        <Link to="/signin" className="navbar-btn signin-btn">
                            Sign In
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
}

export default Navbar;


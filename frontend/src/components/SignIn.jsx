import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './SignIn.css';

function SignIn({ onSwitchToSignUp, onClose }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { signIn } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await signIn(email, password);
            onClose(); // Close modal on success
        } catch (err) {
            setError(err.message || 'Failed to sign in. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form">
            <h2 className="auth-title">Welcome Back</h2>
            <p className="auth-subtitle">Sign in to your account</p>

            <form onSubmit={handleSubmit}>
                {error && (
                    <div className="auth-error">
                        <span className="error-icon">⚠️</span>
                        {error}
                    </div>
                )}

                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        required
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        required
                        disabled={loading}
                    />
                </div>

                <button type="submit" className="auth-submit-btn" disabled={loading}>
                    {loading ? (
                        <>
                            <span className="loading-spinner">⏳</span>
                            Signing in...
                        </>
                    ) : (
                        'Sign In'
                    )}
                </button>
            </form>

            <div className="auth-footer">
                <p>
                    Don't have an account?{' '}
                    <button className="auth-link-btn" onClick={onSwitchToSignUp} disabled={loading}>
                        Sign Up
                    </button>
                </p>
            </div>
        </div>
    );
}

export default SignIn;

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './SignUp.css';

function SignUp({ onSwitchToSignIn, onClose }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const { signUp } = useAuth();

    const getPasswordStrength = (pwd) => {
        if (pwd.length === 0) return { strength: 0, label: '' };
        if (pwd.length < 6) return { strength: 1, label: 'Weak' };
        if (pwd.length < 10) return { strength: 2, label: 'Medium' };
        if (pwd.length >= 10 && /[A-Z]/.test(pwd) && /[0-9]/.test(pwd)) {
            return { strength: 3, label: 'Strong' };
        }
        return { strength: 2, label: 'Medium' };
    };

    const passwordStrength = getPasswordStrength(password);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // Validation
        if (password.length < 6) {
            setError('Password must be at least 6 characters long');
            setLoading(false);
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            await signUp(email, password);
            setSuccess(true);
            // Note: Depending on Supabase settings, user might need to confirm email
            setTimeout(() => {
                onClose();
            }, 2000);
        } catch (err) {
            setError(err.message || 'Failed to create account. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="auth-form">
                <div className="success-message">
                    <span className="success-icon">✅</span>
                    <h2>Account Created!</h2>
                    <p>Check your email to confirm your account.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-form">
            <h2 className="auth-title">Create Account</h2>
            <p className="auth-subtitle">Sign up to get started</p>

            <form onSubmit={handleSubmit}>
                {error && (
                    <div className="auth-error">
                        <span className="error-icon">⚠️</span>
                        {error}
                    </div>
                )}

                <div className="form-group">
                    <label htmlFor="signup-email">Email</label>
                    <input
                        id="signup-email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        required
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="signup-password">Password</label>
                    <input
                        id="signup-password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Create a password"
                        required
                        disabled={loading}
                    />
                    {password && (
                        <div className="password-strength">
                            <div className="strength-bar">
                                <div
                                    className={`strength-fill strength-${passwordStrength.strength}`}
                                    style={{ width: `${(passwordStrength.strength / 3) * 100}%` }}
                                ></div>
                            </div>
                            <span className="strength-label">{passwordStrength.label}</span>
                        </div>
                    )}
                </div>

                <div className="form-group">
                    <label htmlFor="confirm-password">Confirm Password</label>
                    <input
                        id="confirm-password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm your password"
                        required
                        disabled={loading}
                    />
                </div>

                <button type="submit" className="auth-submit-btn" disabled={loading}>
                    {loading ? (
                        <>
                            <span className="loading-spinner">⏳</span>
                            Creating account...
                        </>
                    ) : (
                        'Sign Up'
                    )}
                </button>
            </form>

            <div className="auth-footer">
                <p>
                    Already have an account?{' '}
                    <button className="auth-link-btn" onClick={onSwitchToSignIn} disabled={loading}>
                        Sign In
                    </button>
                </p>
            </div>
        </div>
    );
}

export default SignUp;

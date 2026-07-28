import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { persistSession } from '../utils/auth';

const AuthPage = () => {
    const navigate = useNavigate();
    const [mode, setMode] = useState('signin');
    const [form, setForm] = useState({
        identifier: '',
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'USER'
    });
    const [errorText, setErrorText] = useState('');
    const [statusText, setStatusText] = useState('');
    const [loading, setLoading] = useState(false);

    const extractApiError = (error, fallback) => {
        const data = error?.response?.data;
        if (!error?.response && error?.request) {
            return 'Cannot reach server at http://127.0.0.1:8000. Start the Django backend and try again.';
        }
        if (!data) {
            return fallback;
        }

        if (typeof data === 'string') {
            return data;
        }

        const messages = Object.entries(data).map(([field, value]) => {
            if (Array.isArray(value)) {
                return `${field}: ${value.join(' ')}`;
            }
            return `${field}: ${String(value)}`;
        });

        return messages.length > 0 ? messages.join(' | ') : fallback;
    };

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleRegister = async () => {
        if (form.password !== form.confirmPassword) {
            setErrorText('Passwords do not match.');
            return;
        }

        const username = form.username.trim().toLowerCase();
        const email = form.email.trim().toLowerCase();
        if (!username || !email) {
            setErrorText('Username and email are required for registration.');
            return;
        }

        await api.post('register/', {
            username,
            email,
            password: form.password,
            role: form.role,
        });

        setStatusText('Registration successful. You can now sign in.');
        setMode('signin');
        setForm((prev) => ({ ...prev, identifier: username, password: '', confirmPassword: '' }));
    };

    const handleSignin = async () => {
        const identifier = form.identifier.trim().toLowerCase();
        if (!identifier) {
            setErrorText('Enter your username to sign in.');
            return;
        }

        const response = await api.post('login/', {
            username: identifier,
            password: form.password,
        });
        const session = persistSession(response.data.access, identifier);
        navigate(session.role === 'ADMIN' ? '/admin' : '/dashboard');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorText('');
        setStatusText('');
        setLoading(true);

        try {
            if (mode === 'signin') {
                await handleSignin();
            } else {
                await handleRegister();
            }
        } catch (error) {
            setErrorText(
                extractApiError(
                    error,
                    mode === 'signin' ? 'Sign in failed.' : 'Registration failed.'
                )
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="wire-page">
            <div className="auth-box">
                <h2>User Signup / Login</h2>
                {errorText && <div className="wire-alert bad">{errorText}</div>}
                {statusText && <div className="wire-alert ok">{statusText}</div>}

                <div className="auth-mode-tabs" role="tablist" aria-label="Authentication mode">
                    <button
                        className={`auth-mode-btn ${mode === 'signin' ? 'active' : ''}`}
                        type="button"
                        onClick={() => setMode('signin')}
                    >
                        Sign In
                    </button>
                    <button
                        className={`auth-mode-btn ${mode === 'register' ? 'active' : ''}`}
                        type="button"
                        onClick={() => setMode('register')}
                    >
                        Register
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    {mode === 'signin' ? (
                        <>
                            <label>Username</label>
                            <input
                                type="text"
                                name="identifier"
                                value={form.identifier}
                                onChange={handleChange}
                                required
                            />
                        </>
                    ) : (
                        <>
                            <label>Username</label>
                            <input
                                type="text"
                                name="username"
                                value={form.username}
                                onChange={handleChange}
                                required
                            />

                            <label>Email</label>
                            <input
                                type="email"
                                name="email"
                                value={form.email}
                                onChange={handleChange}
                                required
                            />
                        </>
                    )}

                    <label>Password</label>
                    <input type="password" name="password" value={form.password} onChange={handleChange} required />

                    {mode === 'register' && (
                        <>
                            <label>Confirm password</label>
                            <input
                                type="password"
                                name="confirmPassword"
                                value={form.confirmPassword}
                                onChange={handleChange}
                                required
                            />

                            <label>Account type</label>
                            <select name="role" value={form.role} onChange={handleChange}>
                                <option value="USER">Community Member</option>
                                <option value="EXPERT">Repair Expert</option>
                            </select>
                        </>
                    )}

                    <button className="wire-btn primary submit" type="submit" disabled={loading}>
                        {loading ? 'Please wait...' : mode === 'signin' ? 'Continue to Dashboard' : 'Create Account'}
                    </button>
                </form>
            </div>
        </section>
    );
};

export default AuthPage;

import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const AdminPanel = () => {
    const navigate = useNavigate();
    const [summary, setSummary] = useState({
        users_count: '-',
        submissions_count: '-',
        suggestions_count: '-',
        job_requests_count: '-',
        experts_count: '-',
        verified_experts_count: '-',
        knowledge_entries_count: '-',
    });
    const [experts, setExperts] = useState([]);
    const [errorText, setErrorText] = useState('');
    const [statusText, setStatusText] = useState('');

    const loadData = async () => {
        try {
            const [summaryResponse, expertsResponse] = await Promise.all([
                api.get('admin/dashboard-summary/'),
                api.get('admin/experts/'),
            ]);
            setSummary(summaryResponse.data);
            setExperts(expertsResponse.data);
            setErrorText('');
        } catch {
            setErrorText('Could not load admin data.');
        }
    };

    const setExpertVerification = async (userId, isVerified) => {
        try {
            await api.post(`admin/experts/${userId}/verify/`, { is_verified: isVerified });
            setStatusText(`Expert has been ${isVerified ? 'approved' : 'unapproved'}.`);
            await loadData();
        } catch {
            setErrorText('Could not update expert verification status.');
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            loadData();
        }, 0);
        return () => clearTimeout(timer);
    }, []);

    return (
        <section className="wire-page with-sidebar">
            <aside className="sidebar-box">
                <h3>Admin Navigation</h3>
                <button className="side-link" onClick={() => navigate('/connection-requests')}>View Connection Requests</button>
                <button className="side-link" onClick={() => navigate('/experts')}>View Expert</button>
                <button className="side-link" onClick={() => navigate('/eco-tips')}>View EcoTips</button>
            </aside>

            <div className="panel-main">
                <h2>Admin Dashboard</h2>
                {statusText && <div className="wire-alert ok">{statusText}</div>}
                {errorText && <div className="wire-alert bad">{errorText}</div>}

                <div className="admin-widgets">
                    <article className="widget-card">
                        <h4>Total users</h4>
                        <p>{summary.users_count}</p>
                    </article>
                    <article className="widget-card">
                        <h4>Items uploaded</h4>
                        <p>{summary.submissions_count}</p>
                    </article>
                    <article className="widget-card">
                        <h4>Suggestions log</h4>
                        <p>{summary.suggestions_count}</p>
                    </article>
                    <article className="widget-card">
                        <h4>Connection requests</h4>
                        <p>{summary.job_requests_count}</p>
                    </article>
                    <article className="widget-card">
                        <h4>Connected experts</h4>
                        <p>{summary.experts_count}</p>
                    </article>
                    <article className="widget-card">
                        <h4>Verified experts</h4>
                        <p>{summary.verified_experts_count}</p>
                    </article>
                    <article className="widget-card">
                        <h4>Knowledge base entries</h4>
                        <p>{summary.knowledge_entries_count}</p>
                    </article>
                </div>

                <div className="moderation-box" style={{ marginTop: '0.9rem' }}>
                    <h3>Expert approvals</h3>
                    <p>Approve or unapprove experts before listing confidence is shown to users.</p>
                    <div className="inline-actions" style={{ marginBottom: '0.5rem' }}>
                        <button className="wire-btn" onClick={() => navigate('/experts')}>Open expert directory</button>
                        <button className="wire-btn" onClick={() => navigate('/connection-requests')}>Open request log</button>
                    </div>
                    {experts.map((expert) => (
                        <div className="expert-card" key={expert.id} style={{ marginBottom: '0.55rem' }}>
                            <h4>{expert.username}</h4>
                            <p><strong>Email:</strong> {expert.email}</p>
                            <p><strong>Status:</strong> {expert.is_verified ? 'Verified' : 'Pending verification'}</p>
                            <div className="inline-actions">
                                <button className="wire-btn primary" onClick={() => setExpertVerification(expert.id, true)}>Approve</button>
                                <button className="wire-btn" onClick={() => setExpertVerification(expert.id, false)}>Unapprove</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default AdminPanel;

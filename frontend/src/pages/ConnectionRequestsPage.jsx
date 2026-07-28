import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { getAuthSession } from '../utils/auth';

const ConnectionRequestsPage = () => {
    const { role } = getAuthSession();
    const isExpert = role === 'EXPERT';
    const isAdmin = role === 'ADMIN';

    const [requests, setRequests] = useState([]);
    const [statusText, setStatusText] = useState('');
    const [errorText, setErrorText] = useState('');

    const loadRequests = async () => {
        try {
            const response = await api.get('job-requests/');
            setRequests(response.data);
            setErrorText('');
        } catch {
            setErrorText('Could not load requests.');
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            loadRequests();
        }, 0);
        return () => clearTimeout(timer);
    }, []);

    const respond = async (id, action) => {
        try {
            await api.post(`job-requests/${id}/respond/`, { action });
            setStatusText(`Request #${id} marked as ${action === 'ACCEPT' ? 'accepted' : 'rejected'}.`);
            await loadRequests();
        } catch {
            setErrorText('Could not update request status.');
        }
    };

    const adminAction = async (id, action, note = '') => {
        try {
            await api.post(`job-requests/${id}/admin-action/`, { action, note });
            setStatusText(`Admin action ${action.toLowerCase()} applied to request #${id}.`);
            await loadRequests();
        } catch {
            setErrorText('Could not apply admin action.');
        }
    };

    return (
        <section className="wire-page with-sidebar">
            <div className="panel-main">
                <h2>View Connection Requests</h2>
                <p>Review incoming jobs and manage assignment outcomes.</p>

                {statusText && <div className="wire-alert ok">{statusText}</div>}
                {errorText && <div className="wire-alert bad">{errorText}</div>}

                <div className="admin-widgets">
                    {requests.map((item) => (
                        <article key={item.id} className="widget-card">
                            <h4>Request #{item.id}</h4>
                            <p><strong>Requester:</strong> {item.requester_name}</p>
                            <p><strong>Expert:</strong> {item.expert_name}</p>
                            <p><strong>Status:</strong> {item.status}</p>
                            <p><strong>Message:</strong> {item.message || 'No message.'}</p>

                            {(isExpert || isAdmin) && item.status === 'PENDING' && (
                                <div className="inline-actions">
                                    <button className="wire-btn primary" onClick={() => respond(item.id, 'ACCEPT')}>Accept</button>
                                    <button className="wire-btn" onClick={() => respond(item.id, 'REJECT')}>Reject</button>
                                </div>
                            )}

                            {isAdmin && (
                                <div className="inline-actions">
                                    <button className="wire-btn" onClick={() => adminAction(item.id, 'FLAG')}>Flag</button>
                                    <button className="wire-btn" onClick={() => adminAction(item.id, 'UNFLAG')}>Unflag</button>
                                    <button className="wire-btn" onClick={() => adminAction(item.id, 'ESCALATE')}>Escalate</button>
                                    <button className="wire-btn" onClick={() => adminAction(item.id, 'NOTE', 'Admin intervention logged.')}>Log Note</button>
                                </div>
                            )}
                        </article>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default ConnectionRequestsPage;

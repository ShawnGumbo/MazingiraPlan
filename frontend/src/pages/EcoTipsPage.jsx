import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { getAuthSession } from '../utils/auth';

const EcoTipsPage = () => {
    const { role } = getAuthSession();
    const isAdmin = role === 'ADMIN';

    const [tips, setTips] = useState([]);
    const [draft, setDraft] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editText, setEditText] = useState('');
    const [statusText, setStatusText] = useState('');
    const [errorText, setErrorText] = useState('');

    const loadTips = async () => {
        try {
            const response = await api.get('eco-tips/');
            setTips(response.data);
            setErrorText('');
        } catch {
            setErrorText('Could not load eco tips.');
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            loadTips();
        }, 0);
        return () => clearTimeout(timer);
    }, []);

    const addTip = async () => {
        if (!draft.trim()) return;
        try {
            await api.post('eco-tips/', { content: draft.trim() });
            setDraft('');
            setStatusText('Tip added.');
            await loadTips();
        } catch {
            setErrorText('Could not add tip.');
        }
    };

    const saveEdit = async () => {
        if (!editingId) return;
        try {
            await api.put(`eco-tips/${editingId}/`, { content: editText.trim() });
            setEditingId(null);
            setEditText('');
            setStatusText('Tip updated.');
            await loadTips();
        } catch {
            setErrorText('Could not update tip.');
        }
    };

    const deleteTip = async (id) => {
        try {
            await api.delete(`eco-tips/${id}/`);
            setStatusText('Tip deleted.');
            await loadTips();
        } catch {
            setErrorText('Could not delete tip.');
        }
    };

    return (
        <section className="wire-page with-sidebar">
            <div className="panel-main">
                <h2>View EcoTips</h2>
                <p>Review practical sustainability advice for everyday reuse and disposal decisions.</p>

                {statusText && <div className="wire-alert ok">{statusText}</div>}
                {errorText && <div className="wire-alert bad">{errorText}</div>}

                {isAdmin && (
                    <div className="moderation-box">
                        <h3>Add new tip</h3>
                        <textarea
                            value={draft}
                            onChange={(e) => setDraft(e.target.value)}
                            placeholder="Example: Clean and separate containers before recycling."
                        />
                        <div className="wire-actions end">
                            <button className="wire-btn primary" onClick={addTip}>Add Tip</button>
                        </div>
                    </div>
                )}

                <div className="disposal-grid">
                    {tips.map((tip) => (
                        <article className="disposal-card" key={tip.id}>
                            <h4>Eco Tip #{tip.id}</h4>
                            {editingId === tip.id ? (
                                <>
                                    <textarea value={editText} onChange={(e) => setEditText(e.target.value)} />
                                    <div className="inline-actions">
                                        <button className="wire-btn primary" onClick={saveEdit}>Save</button>
                                        <button className="wire-btn" onClick={() => setEditingId(null)}>Cancel</button>
                                    </div>
                                </>
                            ) : (
                                <p>{tip.content}</p>
                            )}

                            {isAdmin && editingId !== tip.id && (
                                <div className="inline-actions">
                                    <button
                                        className="wire-btn"
                                        onClick={() => {
                                            setEditingId(tip.id);
                                            setEditText(tip.content);
                                        }}
                                    >
                                        Edit
                                    </button>
                                    <button className="wire-btn" onClick={() => deleteTip(tip.id)}>Delete</button>
                                </div>
                            )}
                        </article>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default EcoTipsPage;

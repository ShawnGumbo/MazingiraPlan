import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const MyItemsPage = () => {
    const navigate = useNavigate();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [errorText, setErrorText] = useState('');

    useEffect(() => {
        const fetchItems = async () => {
            try {
                setErrorText('');
                const response = await api.get('my-items/');
                setItems(response.data || []);
            } catch {
                setItems([]);
                setErrorText('Could not load your item history.');
            } finally {
                setLoading(false);
            }
        };

        fetchItems();
    }, []);

    if (loading) {
        return (
            <section className="wire-page with-sidebar">
                <div className="panel-main">
                    <h2>My Repurposing Journey</h2>
                    <p>Loading your previous scans...</p>
                </div>
            </section>
        );
    }

    return (
        <section className="wire-page with-sidebar">
            <div className="panel-main">
                <h2>My Repurposing Journey</h2>
                <p>Review your previous uploads, suggestions, and next best actions.</p>

                {errorText && <div className="wire-alert bad">{errorText}</div>}

                {items.length === 0 ? (
                    <div className="moderation-box">
                        <p>No items yet. Start by uploading your first waste item.</p>
                        <button className="wire-btn primary" onClick={() => navigate('/upload')}>
                            Upload Your First Item
                        </button>
                    </div>
                ) : (
                    <div className="cards-row">
                        {items.map((item) => (
                            <article className="suggestion-card" key={item.id}>
                                <h4>{item.classification_label || item.material_type || 'Waste Item'}</h4>
                                <p><strong>Uploaded:</strong> {new Date(item.created_at).toLocaleString()}</p>
                                <p><strong>Description:</strong> {item.description || 'No description provided.'}</p>
                                <p><strong>Reuse:</strong> {item.repurpose_idea || 'No reuse tip available.'}</p>
                                <p><strong>DIY:</strong> {item.diy_project || 'No DIY guide available.'}</p>
                                <p><strong>Disposal:</strong> {item.disposal_method || 'No disposal guidance available.'}</p>
                                <div className="inline-actions">
                                    <button className="wire-btn" onClick={() => navigate('/experts')}>
                                        Find Expert Help
                                    </button>
                                </div>
                            </article>
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
};

export default MyItemsPage;

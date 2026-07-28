import React from 'react';
import { useNavigate } from 'react-router-dom';

const SuggestionsPage = () => {
    const navigate = useNavigate();
    const raw = sessionStorage.getItem('latest_suggestion');
    const data = raw ? JSON.parse(raw) : null;

    const suggestions = [
        { title: 'Idea 1', content: data?.repurpose_idea || 'Repurposing suggestion will appear here.' },
        { title: 'Idea 2', content: data?.diy_project || 'DIY suggestion will appear here.' },
        { title: 'Idea 3', content: data?.disposal_method || 'Disposal suggestion will appear here.' },
    ];

    return (
        <section className="wire-page with-sidebar">
            <div className="panel-main">
                <h2>AI Suggestions</h2>
                <div className="suggestions-layout">
                    <div className="materials-box">
                        <h3>Identified Materials</h3>
                        <p>{data?.material_type || data?.classification || 'No analyzed item yet.'}</p>
                    </div>

                    <div className="cards-row">
                        {suggestions.map((item) => (
                            <article className="suggestion-card" key={item.title}>
                                <h4>{item.title}</h4>
                                <p>{item.content}</p>
                            </article>
                        ))}
                    </div>
                </div>

                <div className="wire-actions end">
                    <button className="wire-btn primary" onClick={() => navigate('/experts')}>
                        Need Help? Connect with Expert
                    </button>
                </div>
            </div>
        </section>
    );
};

export default SuggestionsPage;

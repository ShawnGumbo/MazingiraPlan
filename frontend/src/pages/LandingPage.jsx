import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuthSession } from '../utils/auth';

const LandingPage = () => {
    const navigate = useNavigate();
    const { isAuthenticated, role } = getAuthSession();

    const primaryRoute = isAuthenticated ? '/dashboard' : '/auth';
    const primaryLabel = isAuthenticated ? 'Open Dashboard' : 'Start With AI';

    const roleCards = [
        {
            title: 'Community Members',
            body: 'Upload an item, get practical reuse guidance, review your item history, and request help from nearby experts.',
            action: () => navigate(primaryRoute),
            actionLabel: 'Get Suggestions',
        },
        {
            title: 'Repair Experts',
            body: 'Show your skills, receive connection requests, and share eco tips to guide local communities.',
            action: () => navigate(isAuthenticated && role === 'EXPERT' ? '/connection-requests' : '/auth'),
            actionLabel: 'Join As Expert',
        },
    ];

    return (
        <section className="wire-page landing-page">
            <div className="landing-hero">
                <p className="landing-kicker">AI Waste Guidance + Community Experts</p>
                <h1>Turn Everyday Waste Into Useful Outcomes</h1>
                <p className="landing-lead">
                    Panolive helps you identify item materials, get practical reuse ideas, and connect with local experts for
                    safer repair and disposal decisions.
                </p>
                <div className="landing-cta-row">
                    <button className="wire-btn primary" onClick={() => navigate(primaryRoute)}>
                        {primaryLabel}
                    </button>
                </div>
                <div className="landing-badges" aria-label="Platform highlights">
                    <span>AI Classification</span>
                    <span>Reuse Ideas</span>
                    <span>Expert Support</span>
                    <span>Trusted Moderation</span>
                </div>
            </div>

            <section className="landing-section">
                <h2>How It Works</h2>
                <div className="landing-steps">
                    <article className="landing-card">
                        <h3>1. Upload</h3>
                        <p>Share an image or description of your item.</p>
                    </article>
                    <article className="landing-card">
                        <h3>2. Analyze</h3>
                        <p>AI identifies likely materials and suggests realistic next steps.</p>
                    </article>
                    <article className="landing-card">
                        <h3>3. Act</h3>
                        <p>Reuse, repurpose, dispose correctly, or request support from experts.</p>
                    </article>
                </div>
            </section>

            <section className="landing-section">
                <h2>Choose Your Path</h2>
                <div className="landing-role-grid">
                    {roleCards.map((card) => (
                        <article className="landing-card role" key={card.title}>
                            <h3>{card.title}</h3>
                            <p>{card.body}</p>
                            <button className="wire-btn" onClick={card.action}>{card.actionLabel}</button>
                        </article>
                    ))}
                </div>
            </section>
        </section>
    );
};

export default LandingPage;

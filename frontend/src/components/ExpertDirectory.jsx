import React, { useEffect, useState } from 'react';
import api from '../services/api';

const ExpertDirectory = () => {
    const [experts, setExperts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusText, setStatusText] = useState('');
    const [errorText, setErrorText] = useState('');
    const [distance, setDistance] = useState('10km');
    const [specialty, setSpecialty] = useState('All');

    const handleRequestHelp = (expert) => {
        const createRequest = async () => {
            try {
                await api.post('job-requests/', {
                    expert: expert.id,
                    message: 'Hello, I would like help repurposing an item from Panolive.'
                });
                setStatusText(`Request sent to ${expert.username}.`);
            } catch {
                setErrorText('Could not send request. Please try again.');
            }
        };

        createRequest();
    };

    useEffect(() => {
        const fetchExperts = async () => {
            try {
                setErrorText('');
                const response = await api.get('experts/');
                setExperts(response.data);
            } catch {
                setExperts([]);
                setErrorText('Could not load experts right now. Please try again shortly.');
            } finally {
                setLoading(false);
            }
        };
        fetchExperts();
    }, []);

    if (loading) {
        return (
            <section className="wire-page with-sidebar">
                <div className="panel-main">
                    <h2>Repair Expert Connect</h2>
                    <p>Loading experts in your area...</p>
                </div>
            </section>
        );
    }

    return (
        <section className="wire-page with-sidebar">
            <div className="panel-main">
                <h2>Repair Expert Connect Page</h2>

                <div className="filter-row">
                    <label>
                        Distance
                        <select value={distance} onChange={(e) => setDistance(e.target.value)}>
                            <option>5km</option>
                            <option>10km</option>
                            <option>20km</option>
                            <option>50km</option>
                        </select>
                    </label>
                    <label>
                        Specialty
                        <select value={specialty} onChange={(e) => setSpecialty(e.target.value)}>
                            <option>All</option>
                            <option>Plastic Repair</option>
                            <option>Metal Repair</option>
                            <option>Electronics</option>
                        </select>
                    </label>
                </div>

                <div className="map-and-list">
                    <div className="map-box">Map Goes Here</div>

                    <div className="expert-actions">
                        {statusText && <div className="wire-alert ok">{statusText}</div>}
                        {errorText && <div className="wire-alert bad">{errorText}</div>}

                        {experts.length > 0 ? (
                            experts.map((expert) => (
                                <div key={expert.id} className="expert-card">
                                    <h4>{expert.username}</h4>
                                    <p><strong>Contact:</strong> {expert.email}</p>
                                    <p><strong>Skills:</strong> {expert.skills || 'General repairs'}</p>
                                    <p><strong>Rating:</strong> {expert.rating || 0} / 5</p>
                                    <button className="wire-btn" onClick={() => handleRequestHelp(expert)}>
                                        Contact {expert.username}
                                    </button>
                                </div>
                            ))
                        ) : (
                            <p>No experts available.</p>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ExpertDirectory;

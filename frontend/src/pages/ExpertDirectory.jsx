import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import { getAuthSession } from '../utils/auth';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

const DEFAULT_CENTER = [-1.286389, 36.817223]; // Nairobi

const ExpertDirectory = () => {
    const navigate = useNavigate();
    const { isAuthenticated } = getAuthSession();
    const [experts, setExperts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusText, setStatusText] = useState('');
    const [errorText, setErrorText] = useState('');
    const [distance, setDistance] = useState('10km');
    const [specialty, setSpecialty] = useState('All');

    const handleRequestHelp = (expert) => {
        if (!isAuthenticated) {
            navigate('/auth');
            return;
        }

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
        <section className="wire-page experts-module">
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
                    <div className="map-box">
                        <MapContainer center={DEFAULT_CENTER} zoom={11} zoomControl scrollWheelZoom className="leaflet-map">
                            <TileLayer
                                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />
                            <Marker position={DEFAULT_CENTER}>
                                <Popup>
                                    <strong>Panolive Service Area</strong>
                                    <br />
                                    Nairobi, Kenya
                                </Popup>
                            </Marker>
                            {experts.map((expert, index) => {
                                const latOffset = (index % 4) * 0.015;
                                const lngOffset = Math.floor(index / 4) * 0.015;
                                const position = [DEFAULT_CENTER[0] + latOffset, DEFAULT_CENTER[1] + lngOffset];

                                return (
                                    <Marker key={expert.id} position={position}>
                                        <Popup>
                                            <strong>{expert.username}</strong>
                                            <br />
                                            {expert.skills && expert.skills.length > 0 ? expert.skills.join(', ') : 'General repairs'}
                                            <br />
                                            {expert.email}
                                        </Popup>
                                    </Marker>
                                );
                            })}
                        </MapContainer>
                    </div>

                    <div className="expert-actions">
                        {statusText && <div className="wire-alert ok">{statusText}</div>}
                        {errorText && <div className="wire-alert bad">{errorText}</div>}

                        {experts.length > 0 ? (
                            experts.map((expert) => (
                                <div key={expert.id} className="expert-card">
                                    <h4>{expert.username}</h4>
                                    <p><strong>Contact:</strong> {expert.email}</p>
                                    <p>
                                        <strong>Skills:</strong>{' '}
                                        {Array.isArray(expert.skills)
                                            ? (expert.skills.length > 0 ? expert.skills.join(', ') : 'General repairs')
                                            : (expert.skills || 'General repairs')}
                                    </p>
                                    <p><strong>Rating:</strong> {expert.rating || 0} / 5</p>
                                    <button className="wire-btn" onClick={() => handleRequestHelp(expert)}>
                                        {isAuthenticated ? `Contact ${expert.username}` : 'Sign In to Contact'}
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

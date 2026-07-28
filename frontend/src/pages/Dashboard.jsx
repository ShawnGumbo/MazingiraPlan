import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuthSession } from '../utils/auth';

const Dashboard = () => {
    const navigate = useNavigate();

    const { role: userRole, username: sessionUsername } = getAuthSession();
    const username = sessionUsername || 'friend';

    return (
        <section className="wire-page with-sidebar">
            <aside className="sidebar-box">
                <h3>Navigation</h3>
                {userRole === 'USER' && (
                    <>
                        <button className="side-link" onClick={() => navigate('/upload')}>Upload Item</button>
                        <button className="side-link" onClick={() => navigate('/my-items')}>My Items History</button>
                        <button className="side-link" onClick={() => navigate('/experts')}>Expert Directory</button>
                        <button className="side-link" onClick={() => navigate('/eco-tips')}>View EcoTips</button>
                    </>
                )}
                {userRole === 'EXPERT' && (
                    <button className="side-link" onClick={() => navigate('/connection-requests')}>View Connection Requests</button>
                )}
                {userRole === 'ADMIN' && (
                    <>
                        <button className="side-link" onClick={() => navigate('/connection-requests')}>View Connection Requests</button>
                        <button className="side-link" onClick={() => navigate('/experts')}>View Expert</button>
                        <button className="side-link" onClick={() => navigate('/eco-tips')}>View EcoTips</button>
                    </>
                )}
            </aside>

            <div className="panel-main">
                <h2>{userRole === 'ADMIN' ? 'Administrator Dashboard' : userRole === 'EXPERT' ? 'Repair Expert Dashboard' : 'Community Dashboard'}</h2>
                <p>Welcome back, {username}.</p>
                <p>Signed in role: {userRole || 'USER'}</p>

                <h3>Quick-start guide</h3>
                <ul className="wire-list">
                    {userRole === 'USER' && <li>Upload an item image and description to trigger AI material analysis.</li>}
                    {userRole === 'USER' && <li>Open My Items History to review your previous scans and suggestions.</li>}
                    {userRole === 'USER' && <li>Open Expert Directory to browse profiles with skill and contact details.</li>}
                    {userRole === 'USER' && <li>Read EcoTips to adopt practical sustainable habits.</li>}

                    {userRole === 'EXPERT' && <li>Open View Connection Requests to inspect incoming jobs.</li>}
                    {userRole === 'EXPERT' && <li>Accept jobs that match your capacity and reject those unavailable.</li>}

                    {userRole === 'ADMIN' && <li>Review all connection requests and intervene when required.</li>}
                    {userRole === 'ADMIN' && <li>Manage expert visibility and monitor profile data.</li>}
                    {userRole === 'ADMIN' && <li>Add, edit, and delete EcoTips for quality assurance.</li>}
                </ul>
            </div>
        </section>
    );
};

export default Dashboard;

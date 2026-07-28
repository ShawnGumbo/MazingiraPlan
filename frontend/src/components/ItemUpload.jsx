import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const ItemUpload = () => {
    const navigate = useNavigate();
    const [image, setImage] = useState(null);
    const [description, setDescription] = useState('');
    const [previewUrl, setPreviewUrl] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errorText, setErrorText] = useState('');

    useEffect(() => {
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        };
    }, [previewUrl]);

    const handleFileChange = (e) => {
        const file = e.target.files?.[0] || null;

        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }

        setImage(file);
        setResult(null);
        setErrorText('');

        if (!file) {
            setPreviewUrl('');
            return;
        }

        setPreviewUrl(URL.createObjectURL(file));
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrorText('');
        setResult(null);
        
        const formData = new FormData();
        formData.append('image', image);
        formData.append('description', description || 'A waste item');

        try {
            const response = await api.post('submit-item/', formData, {
                headers: { 
                    'Content-Type': 'multipart/form-data',
                }
            });
            sessionStorage.setItem('latest_suggestion', JSON.stringify(response.data));
            setResult(response.data);
            navigate('/suggestions');
        } catch {
            setErrorText('Upload failed. Please log in and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="wire-page with-sidebar">
            <div className="panel-main">
                <h2>Upload Item Page</h2>

                <form className="wire-upload-form" onSubmit={handleUpload}>
                    {errorText && <div className="wire-alert bad">{errorText}</div>}

                    <label className="drop-area" htmlFor="item-photo">
                        <span>Drag and drop an image here</span>
                        <input
                            id="item-photo"
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            required
                            hidden
                        />
                    </label>

                    {previewUrl && <img className="preview" src={previewUrl} alt="Selected waste item preview" />}

                    <label htmlFor="description">Description (optional)</label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Example: Cracked plastic bucket with broken handle"
                    />

                    <button className="wire-btn primary submit" type="submit" disabled={loading || !image}>
                        {loading ? 'Analyzing...' : 'Analyze Item'}
                    </button>
                </form>

                {result && <p className="wire-note">Analysis completed. Opening suggestions page.</p>}
            </div>
        </section>
    );
};

export default ItemUpload;

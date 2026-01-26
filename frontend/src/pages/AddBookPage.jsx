import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { createBook } from '../services/api';
import { supabase } from '../services/supabaseClient';
import './AddBookPage.css';

function AddBookPage() {
    const { user, loading: authLoading } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const [formData, setFormData] = useState({
        isbn13: '',
        title: '',
        authors: '',
        categories: '',
        description: '',
        thumbnail: '',
        average_rating: '',
        num_pages: '',
        published_year: '',
    });

    // Redirect if not logged in
    useEffect(() => {
        if (!authLoading && !user) {
            navigate('/signin');
        }
    }, [user, authLoading, navigate]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Get the session token
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                throw new Error('No active session');
            }

            // Prepare book data
            const bookData = {
                isbn13: parseInt(formData.isbn13, 10),
                title: formData.title || null,
                authors: formData.authors || null,
                categories: formData.categories || null,
                description: formData.description,
                thumbnail: formData.thumbnail || null,
                average_rating: formData.average_rating ? parseFloat(formData.average_rating) : null,
                num_pages: formData.num_pages ? parseInt(formData.num_pages, 10) : null,
                published_year: formData.published_year ? parseInt(formData.published_year, 10) : null,
            };

            await createBook(bookData, session.access_token);
            setSuccess(true);

            // Reset form
            setFormData({
                isbn13: '',
                title: '',
                authors: '',
                categories: '',
                description: '',
                thumbnail: '',
                average_rating: '',
                num_pages: '',
                published_year: '',
            });
        } catch (err) {
            setError(err.message || 'Failed to add book. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (authLoading) {
        return (
            <div className="add-book-page">
                <div className="add-book-loading">
                    <span className="loading-spinner-large">⏳</span>
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="add-book-page">
            <div className="add-book-container">
                <div className="add-book-header">
                    <Link to="/" className="add-book-back-link">
                        <span className="back-arrow">←</span> Back to Home
                    </Link>
                </div>

                <div className="add-book-form-wrapper">
                    {success ? (
                        <div className="add-book-success">
                            <span className="success-icon">✅</span>
                            <h2>Book Added Successfully!</h2>
                            <p>Your book has been added to the library.</p>
                            <button
                                className="add-another-btn"
                                onClick={() => setSuccess(false)}
                            >
                                Add Another Book
                            </button>
                        </div>
                    ) : (
                        <div className="add-book-form">
                            <h2 className="add-book-title">Add a New Book</h2>
                            <p className="add-book-subtitle">Share a book with the community</p>

                            <form onSubmit={handleSubmit}>
                                {error && (
                                    <div className="add-book-error">
                                        <span className="error-icon">⚠️</span>
                                        {error}
                                    </div>
                                )}

                                <div className="form-row">
                                    <div className="form-group">
                                        <label htmlFor="isbn13">ISBN-13 *</label>
                                        <input
                                            id="isbn13"
                                            name="isbn13"
                                            type="number"
                                            value={formData.isbn13}
                                            onChange={handleChange}
                                            placeholder="Enter 13-digit ISBN"
                                            required
                                            disabled={loading}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="title">Title</label>
                                        <input
                                            id="title"
                                            name="title"
                                            type="text"
                                            value={formData.title}
                                            onChange={handleChange}
                                            placeholder="Enter book title"
                                            disabled={loading}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label htmlFor="authors">Authors</label>
                                        <input
                                            id="authors"
                                            name="authors"
                                            type="text"
                                            value={formData.authors}
                                            onChange={handleChange}
                                            placeholder="e.g. John Doe, Jane Smith"
                                            disabled={loading}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="categories">Categories</label>
                                        <input
                                            id="categories"
                                            name="categories"
                                            type="text"
                                            value={formData.categories}
                                            onChange={handleChange}
                                            placeholder="e.g. Fiction, Mystery"
                                            disabled={loading}
                                        />
                                    </div>
                                </div>

                                <div className="form-group full-width">
                                    <label htmlFor="description">Description *</label>
                                    <textarea
                                        id="description"
                                        name="description"
                                        value={formData.description}
                                        onChange={handleChange}
                                        placeholder="Enter a brief description of the book..."
                                        rows="4"
                                        required
                                        disabled={loading}
                                    />
                                </div>

                                <div className="form-group full-width">
                                    <label htmlFor="thumbnail">Thumbnail URL</label>
                                    <input
                                        id="thumbnail"
                                        name="thumbnail"
                                        type="url"
                                        value={formData.thumbnail}
                                        onChange={handleChange}
                                        placeholder="https://example.com/book-cover.jpg"
                                        disabled={loading}
                                    />
                                </div>

                                <div className="form-row three-cols">
                                    <div className="form-group">
                                        <label htmlFor="average_rating">Rating (0-5)</label>
                                        <input
                                            id="average_rating"
                                            name="average_rating"
                                            type="number"
                                            step="0.1"
                                            min="0"
                                            max="5"
                                            value={formData.average_rating}
                                            onChange={handleChange}
                                            placeholder="e.g. 4.5"
                                            disabled={loading}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="num_pages">Pages</label>
                                        <input
                                            id="num_pages"
                                            name="num_pages"
                                            type="number"
                                            min="1"
                                            value={formData.num_pages}
                                            onChange={handleChange}
                                            placeholder="e.g. 350"
                                            disabled={loading}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="published_year">Year</label>
                                        <input
                                            id="published_year"
                                            name="published_year"
                                            type="number"
                                            min="1000"
                                            max="2100"
                                            value={formData.published_year}
                                            onChange={handleChange}
                                            placeholder="e.g. 2024"
                                            disabled={loading}
                                        />
                                    </div>
                                </div>

                                <button type="submit" className="add-book-submit-btn" disabled={loading}>
                                    {loading ? (
                                        <>
                                            <span className="loading-spinner">⏳</span>
                                            Adding Book...
                                        </>
                                    ) : (
                                        <>
                                            <span className="btn-icon">📖</span>
                                            Add Book
                                        </>
                                    )}
                                </button>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default AddBookPage;

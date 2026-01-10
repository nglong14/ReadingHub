import React from 'react';
import EmotionBadge from './EmotionBadge';
import './BookCard.css';

const BookCard = ({ book }) => {
    const emotions = [
        { name: 'joy', value: book.joy },
        { name: 'sadness', value: book.sadness },
        { name: 'anger', value: book.anger },
        { name: 'fear', value: book.fear },
        { name: 'surprise', value: book.surprise },
        { name: 'disgust', value: book.disgust },
        { name: 'neutral', value: book.neutral },
    ];

    // Truncate description
    const truncateText = (text, maxLength = 300) => {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    // Render star rating
    const renderStars = (rating) => {
        if (!rating) return null;
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const stars = [];

        for (let i = 0; i < fullStars; i++) {
            stars.push(<span key={`full-${i}`}>★</span>);
        }
        if (hasHalfStar && fullStars < 5) {
            stars.push(<span key="half">★</span>);
        }
        const emptyStars = 5 - stars.length;
        for (let i = 0; i < emptyStars; i++) {
            stars.push(<span key={`empty-${i}`} style={{ color: '#DDD' }}>★</span>);
        }

        return stars;
    };

    return (
        <div className="book-card">
            <div className="book-card-inner">
                <div className="book-thumbnail">
                    {book.thumbnail ? (
                        <img src={book.thumbnail} alt={book.title} onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                        }} />
                    ) : null}
                    <div className="book-placeholder" style={{ display: book.thumbnail ? 'none' : 'flex' }}>
                        <span>📚</span>
                    </div>
                </div>

                <div className="book-content">
                    <h3 className="book-title">{book.title}</h3>

                    <p className="book-authors">
                        <span className="icon">by</span>
                        {book.authors || 'Unknown Author'}
                    </p>

                    {book.categories && (
                        <p className="book-category">
                            <span className="icon">📚</span>
                            {book.categories}
                        </p>
                    )}

                    <div className="book-meta">
                        {book.average_rating && (
                            <span className="meta-item star-rating">
                                {renderStars(book.average_rating)}
                                <span style={{ marginLeft: '0.3rem', color: 'var(--goodreads-text)' }}>
                                    {book.average_rating.toFixed(2)}
                                </span>
                            </span>
                        )}
                        {book.published_year && (
                            <span className="meta-item">
                                Published {book.published_year}
                            </span>
                        )}
                        {book.num_pages && (
                            <span className="meta-item">
                                {book.num_pages} pages
                            </span>
                        )}
                    </div>

                    <p className="book-description">
                        {truncateText(book.description)}
                    </p>

                    <div className="emotion-container">
                        {emotions.map(({ name, value }) => (
                            <EmotionBadge key={name} emotion={name} value={value} />
                        ))}
                    </div>

                    <div className="relevance-score">
                        <span className="score-label">Match:</span>
                        <span className="score-value">{(book.score * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BookCard;

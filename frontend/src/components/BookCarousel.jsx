import { useState } from 'react';
import './BookCarousel.css';

function BookCarousel({ books }) {
    const [currentIndex, setCurrentIndex] = useState(0);

    if (!books || books.length === 0) {
        return null;
    }

    const handlePrevious = () => {
        setCurrentIndex((prevIndex) =>
            prevIndex === 0 ? books.length - 1 : prevIndex - 1
        );
    };

    const handleNext = () => {
        setCurrentIndex((prevIndex) =>
            prevIndex === books.length - 1 ? 0 : prevIndex + 1
        );
    };

    const currentBook = books[currentIndex];

    return (
        <div className="carousel-container">
            <h2 className="carousel-title">
                Book {currentIndex + 1} of {books.length}
            </h2>

            <div className="carousel-wrapper">
                <button
                    className="carousel-nav-btn prev-btn"
                    onClick={handlePrevious}
                    aria-label="Previous book"
                >
                    ‹
                </button>

                <div className="carousel-book-display">
                    <div className="book-cover-wrapper">
                        {currentBook.thumbnail ? (
                            <img
                                src={currentBook.thumbnail}
                                alt={currentBook.title || 'Book cover'}
                                className="carousel-book-cover"
                            />
                        ) : (
                            <div className="carousel-book-placeholder">
                                <span className="placeholder-icon">📖</span>
                                <p>No Cover Available</p>
                            </div>
                        )}
                    </div>

                    <div className="carousel-book-info">
                        <h3 className="carousel-book-title">
                            {currentBook.title || 'Unknown Title'}
                        </h3>
                        <p className="carousel-book-author">
                            by {currentBook.authors || 'Unknown Author'}
                        </p>
                        {currentBook.average_rating && (
                            <div className="carousel-rating">
                                <span className="rating-stars">⭐</span>
                                <span className="rating-value">{currentBook.average_rating}</span>
                            </div>
                        )}
                        {currentBook.description && (
                            <p className="carousel-description">
                                {currentBook.description.length > 200
                                    ? currentBook.description.substring(0, 200) + '...'
                                    : currentBook.description}
                            </p>
                        )}
                    </div>
                </div>

                <button
                    className="carousel-nav-btn next-btn"
                    onClick={handleNext}
                    aria-label="Next book"
                >
                    ›
                </button>
            </div>

            <div className="carousel-indicators">
                {books.map((_, index) => (
                    <button
                        key={index}
                        className={`indicator-dot ${index === currentIndex ? 'active' : ''}`}
                        onClick={() => setCurrentIndex(index)}
                        aria-label={`Go to book ${index + 1}`}
                    />
                ))}
            </div>
        </div>
    );
}

export default BookCarousel;

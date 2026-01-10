import { useState } from 'react';
import SearchBar from './components/SearchBar';
import BookCard from './components/BookCard';
import { searchBooks } from './services/api';
import './App.css';

function App() {
  const [books, setBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (query) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const data = await searchBooks(query, 12);
      setBooks(data.results || []);
    } catch (err) {
      setError('Failed to search books. Please make sure the backend is running.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="app-container">
        <header className="app-header">
          <h1 className="app-title">
            <span className="title-icon">📚</span>
            Book Recommendation
          </h1>
          <p className="app-subtitle">
            Discover your next favorite book with AI-powered emotional analysis
          </p>
        </header>

        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {isLoading && (
          <div className="loading-container">
            <div className="loading-spinner-large">⏳</div>
            <p className="loading-text">Searching for books...</p>
          </div>
        )}

        {!isLoading && hasSearched && books.length === 0 && !error && (
          <div className="no-results">
            <span className="no-results-icon">🔍</span>
            <p>No books found. Try a different search query.</p>
          </div>
        )}

        {!isLoading && books.length > 0 && (
          <>
            <div className="results-header">
              <h2 className="results-title">
                Found {books.length} book{books.length !== 1 ? 's' : ''}
              </h2>
            </div>
            <div className="books-grid">
              {books.map((book, index) => (
                <BookCard key={`${book.isbn13}-${index}`} book={book} />
              ))}
            </div>
          </>
        )}

        {!hasSearched && (
          <div className="welcome-message">
            <div className="welcome-icon">✨</div>
            <h2>Welcome to Book Recommendation</h2>
            <p>Search for books and discover emotional insights</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

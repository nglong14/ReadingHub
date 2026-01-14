import { useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import SearchBar from './components/SearchBar';
import BookCarousel from './components/BookCarousel';
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
      const data = await searchBooks(query, 10);
      setBooks(data.results || []);
    } catch (err) {
      setError('Failed to search books. Please make sure the backend is running.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthProvider>
      <div className="app">
        <Navbar />

        <div className="app-container">
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
              <BookCarousel books={books} />

              <div className="results-header">
                <h2 className="results-title">
                  All {books.length} Result{books.length !== 1 ? 's' : ''}
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
    </AuthProvider>
  );
}

export default App;


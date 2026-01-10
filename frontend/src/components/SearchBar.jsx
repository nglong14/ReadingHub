import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch, isLoading }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    const handleChange = (e) => {
        setQuery(e.target.value);
    };

    return (
        <div className="search-bar-container">
            <form onSubmit={handleSubmit} className="search-form">
                <div className="search-input-wrapper">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search for books by title, author, or description..."
                        value={query}
                        onChange={handleChange}
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        className="search-button"
                        disabled={isLoading || !query.trim()}
                    >
                        {isLoading ? (
                            <span className="loading-spinner">⏳</span>
                        ) : (
                            'Search'
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default SearchBar;

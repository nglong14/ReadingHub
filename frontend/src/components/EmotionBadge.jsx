import React from 'react';
import './EmotionBadge.css';

const EmotionBadge = ({ emotion, value }) => {
    // Only show emotions with significant values (> 0.3)
    if (!value || value < 0.3) return null;

    const emotionColors = {
        joy: '#FFD700',
        sadness: '#4A90E2',
        anger: '#E74C3C',
        fear: '#9B59B6',
        surprise: '#F39C12',
        disgust: '#16A085',
        neutral: '#95A5A6',
    };

    const emotionEmojis = {
        joy: '😊',
        sadness: '😢',
        anger: '😠',
        fear: '😨',
        surprise: '😲',
        disgust: '🤢',
        neutral: '😐',
    };

    const percentage = Math.round(value * 100);

    return (
        <div
            className="emotion-badge"
            style={{
                '--emotion-color': emotionColors[emotion] || '#95A5A6',
                '--emotion-opacity': value
            }}
        >
            <span className="emotion-emoji">{emotionEmojis[emotion]}</span>
            <span className="emotion-name">{emotion}</span>
            <span className="emotion-value">{percentage}%</span>
        </div>
    );
};

export default EmotionBadge;

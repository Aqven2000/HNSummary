import React, { useState, useEffect } from 'react';
import './TopStories.css'; // Correct import for the CSS file
import axios from 'axios';

function TopStories() {
    const [stories, setStories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // fetch('/api/summaries')
        //     .then(response => {
        //         if (!response.ok) {
        //             throw new Error('Network response was not ok');
        //         }
        //         return response;
        //     })
        //     .then(data => {
        //         setStories(data);
        //         setLoading(false);
        //     })
        //     .catch(err => {
        //         setError(err);
        //         setLoading(false);
        //     });

        axios.get('http://127.0.0.1:5000/api/summaries')
            .then(response => {
                setStories(response.data); // Set fetched stories
                setLoading(false); // Set loading to false after fetching
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                setError(error); // Capture error for display
                setLoading(false); // Also set loading to false on error
            });

    }, []);

    return (
        <div className="container">
            <h1 className="header-title">Top Hacker News Summaries</h1>
            {loading && <p className="loading-message">Loading summaries...</p>}
            {error && <p className="error-message">Error loading summaries: {error.message}</p>}
            {stories.map(story => (
                <div key={story.id} className="story-card">
                    <div className="story-header">
                        <a href={story.url} className="story-title" target="_blank" rel="noopener noreferrer">
                            {story.title}
                        </a>
                    </div>
                    <p className="story-summary">{story.summary}</p>
                </div>
            ))}
                <div class="footer">
                    <p>Powered by <a href="https://news.ycombinator.com/" target="_blank">Hacker News</a> & OpenAI Summarization</p>
                </div>
        </div>    
    );
}

export default TopStories;

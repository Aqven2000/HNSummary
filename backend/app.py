from flask import Flask, jsonify , render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key using environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

HN_TOP_STORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HN_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'

def get_top_stories(limit=1):
    try:
        response = requests.get(HN_TOP_STORIES_URL)
        response.raise_for_status()
        top_story_ids = response.json()[:limit]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching top stories: {e}")
        return []  # Return an empty list on error

    stories = []
    for story_id in top_story_ids:
        try:
            story_response = requests.get(HN_ITEM_URL.format(story_id))
            story_response.raise_for_status()
            story_data = story_response.json()
            if story_data and 'url' in story_data:
                full_html = extract_full_html_from_url(story_data['url'])
                summary = summarize_html(full_html) if full_html else "Text extraction failed or not available."
                stories.append({
                    "id": story_data['id'],
                    "title": story_data['title'],
                    "url": story_data['url'],
                    "summary": summary
                })
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching story {story_id}: {e}")

    return stories

def extract_full_html_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract main content from specific tags if available
        main_content = soup.find('article')
        if not main_content:
            main_content = soup.find('main') or soup.find('div', {'id': 'content'})

        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)

        # Trim the text to the most relevant portion (e.g., first 1500 characters)
        return ' '.join(text.split()[:500])  # Extract the first 500 words

    except Exception as e:
        print(f"Failed to extract HTML from {url}: {e}")
        return None

def summarize_html(html_content):
    if not html_content:
        return "No HTML to summarize."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Please summarize the following text, highlighting the main ideas and key points:\n\n{html_content}"}],
            max_tokens=150  # Adjust based on how concise you want the summary to be
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Summarization failed."

@app.route('/api/summaries', methods=['GET'])
def get_summaries():
    top_stories = get_top_stories(limit=5)
    return jsonify(top_stories)
    #return render_template('index.html', stories=top_stories)

if __name__ == '__main__':
    app.run(debug=True)

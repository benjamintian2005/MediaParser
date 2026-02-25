from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def parse_letterboxd(url):
    try:
        # Remove any existing page parameter
        url += "/films"
        base_url = url.split('?')[0]
        page = 1
        all_reviews = []
        
        while True:
            # Add page parameter to URL
            page_url = f"{base_url}/page/{page}/" if page > 1 else base_url
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all review entries
            reviews = []
            for review in soup.find_all('li', class_='poster-container'):
                # Find the film poster div
                poster_div = review.find('div', class_='linked-film-poster')
                if poster_div:
                    # Get the title from the img alt attribute
                    img = poster_div.find('img')
                    if img and img.get('alt'):
                        # Get the rating from the poster-viewingdata paragraph
                        rating_span = review.find('p', class_='poster-viewingdata')
                        rating = 'No rating'
                        if rating_span:
                            rating_element = rating_span.find('span', class_='rating')
                            if rating_element:
                                rating = rating_element.text.strip()
                        
                        reviews.append({
                            'title': img['alt'],
                            'rating': rating,
                            'platform': 'Letterboxd'
                        })
            
            if not reviews:  # No more reviews found
                break
                
            all_reviews.extend(reviews)
            page += 1
            
            # Optional: Limit to first 5 pages to prevent too many requests
            #if page > 5: break
        
        if len(all_reviews) == 0:
            return {'error': 'No reviews found. Please make sure the profile is public and contains reviews.'}
        return all_reviews
    except Exception as e:
        return {'error': f'Error parsing Letterboxd: {str(e)}'}

def parse_goodreads(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []

        # Find all book reviews
        for review in soup.find_all('tr', class_='bookalike review'):
            title = review.find('td', class_='field title')
            if title:
                reviews.append({
                    'title': title.text.strip(),
                    'platform': 'Goodreads'
                })
        return reviews
    except Exception as e:
        return {'error': str(e)}

def parse_rateyourmusic(url):
    try:
        match = re.search(r'rateyourmusic\.com/~([^/?]+)', url)
        if not match:
            return {'error': 'Could not extract username. Use format: https://rateyourmusic.com/~username'}

        username = match.group(1)
        base_url = f'https://rateyourmusic.com/collection/{username}/r/'
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; MediaParser/1.0)'}
        page = 1
        all_reviews = []

        while True:
            page_url = f'{base_url}{page}/' if page > 1 else base_url
            response = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            reviews = []
            for item in soup.find_all('div', class_='or_q_albumartist'):
                title_tag = item.find('a', class_='album')
                if not title_tag:
                    continue
                title = title_tag.text.strip()

                artist_tag = item.find('a', class_='artist')
                artist = artist_tag.text.strip() if artist_tag else ''

                rating_tag = item.find(class_='rating_num')
                rating = rating_tag.text.strip() if rating_tag else 'No rating'

                reviews.append({
                    'title': f'{artist} - {title}' if artist else title,
                    'rating': rating,
                    'platform': 'RateYourMusic'
                })

            if not reviews:
                break

            all_reviews.extend(reviews)
            page += 1

        if not all_reviews:
            return {'error': 'No ratings found. Make sure the profile is public and contains ratings.'}
        return all_reviews
    except Exception as e:
        return {'error': f'Error parsing RateYourMusic: {str(e)}'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json()
    url = data.get('url', '')
    
    if 'letterboxd.com' in url:
        results = parse_letterboxd(url)
    elif 'goodreads.com' in url:
        results = parse_goodreads(url)
    elif 'rateyourmusic.com' in url:
        results = parse_rateyourmusic(url)
    else:
        results = {'error': 'Unsupported platform'}
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 
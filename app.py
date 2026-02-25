from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def parse_letterboxd(url):
    try:
        match = re.search(r'letterboxd\.com/([^/?#]+)', url)
        if not match:
            return {'error': 'Could not extract username from URL.'}
        username = match.group(1)

        rss_url = f'https://letterboxd.com/{username}/rss/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(rss_url, headers=headers)
        if response.status_code != 200:
            return {'error': f'Could not fetch Letterboxd RSS feed (status {response.status_code}).'}

        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []
        for item in soup.find_all('item'):
            title_tag = item.find('letterboxd:filmtitle')
            rating_tag = item.find('letterboxd:memberrating')
            year_tag = item.find('letterboxd:filmyear')
            if not title_tag:
                continue
            title = title_tag.text.strip()
            if year_tag:
                title += f' ({year_tag.text.strip()})'
            rating = rating_tag.text.strip() if rating_tag else 'No rating'
            reviews.append({'title': title, 'rating': rating, 'platform': 'Letterboxd'})

        if not reviews:
            return {'error': 'No entries found. Make sure the profile is public and has diary entries.'}
        return reviews
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

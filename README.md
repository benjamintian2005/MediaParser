# MediaParser

A lightweight web app that aggregates your media ratings across Letterboxd, Goodreads, and RateYourMusic into a single view. Paste in a profile URL and it scrapes your logged films, books, or albums and displays them with their ratings, grouped by platform.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

## How it works

1. Paste a profile URL into the input field
2. The app detects the platform from the URL and fetches your data
3. Results are displayed as a list of titles and ratings, grouped by platform

## Supported platforms

### Letterboxd
Paste any URL from your Letterboxd profile — the app extracts your username and pulls your diary entries via the RSS feed, returning film titles, release years, and your star ratings.

Examples:
- `https://letterboxd.com/username/`
- `https://letterboxd.com/username/films/`
- `https://letterboxd.com/username/films/page/1/#/`

> Note: Letterboxd's RSS feed is capped at your 50 most recent diary entries.

### Goodreads
Paste your Goodreads profile or shelf URL. Returns book titles from your read shelf. Rating extraction is not yet implemented.

Example: `https://www.goodreads.com/review/list/username`

### RateYourMusic
Paste your RateYourMusic profile URL using the `~username` format. The app paginates through your full ratings collection, returning artist, album, and your numeric rating.

Example: `https://rateyourmusic.com/~username`

> Note: Your RateYourMusic profile must be set to public, otherwise no results will be returned.

## Stack

- **Backend:** Python / Flask
- **Scraping:** requests + BeautifulSoup4
- **Frontend:** Vanilla JS + Jinja2 template

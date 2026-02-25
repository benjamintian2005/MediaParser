# MediaParser

Paste in your profile URL from Letterboxd, Goodreads, or RateYourMusic and see all your ratings in one place. That's pretty much it.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then go to `http://localhost:5000`.

## Supported sites

- **Letterboxd** — paste your profile URL (e.g. `letterboxd.com/username`)
- **Goodreads** — paste your profile URL (titles only for now, ratings coming)
- **RateYourMusic** — paste your profile URL (e.g. `rateyourmusic.com/~username`)

## Notes

RateYourMusic profiles need to be set to public. If you get no results, that's usually why.

Letterboxd pulls every page of your films list, so it can take a moment if you've logged a lot.

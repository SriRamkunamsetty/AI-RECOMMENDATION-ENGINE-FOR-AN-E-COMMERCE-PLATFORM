# AI Recommendation Engine for an E-Commerce Platform

This project is a Python/Reflex e-commerce prototype that combines rating-based, collaborative, and TF-IDF content-based recommendations with catalog search, Firebase authentication, a cart, wishlist, checkout, order history, and an optional Groq shopping assistant.

## Requirements

Use Python 3.11 or newer and install the pinned dependencies:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the repository root. Firebase variables are required for authentication, cart, wishlist, search-history, and order persistence. The Groq key is optional and only enables the AI assistant.

```env
FIREBASE_API_KEY=your-value
FIREBASE_AUTH_DOMAIN=your-value
FIREBASE_PROJECT_ID=your-value
FIREBASE_STORAGE_BUCKET=your-value
FIREBASE_SENDER_ID=your-value
FIREBASE_APP_ID=your-value
FIREBASE_DATABASE_URL=your-value
GROQ_API_KEY=your-value
GROQ_MODEL=llama-3.1-8b-instant
```

Never commit `.env`, Firebase secrets, Groq keys, or payment credentials. The repository uses a clearly labelled local demo payment flow; it does not perform a real charge.

## Prepare the dataset

The raw dataset is `clean_data.csv`. To regenerate the runtime dataset and remove invalid sentinel identifiers, run this command from any working directory:

```bash
python -m backend.cleaning_data
```

The output is written to the repository’s `cleaned_data.csv` path.

## Run the application

Start the Reflex development server from the repository root:

```bash
reflex run
```

Then open the URL printed by Reflex, normally `http://localhost:3000`. Running `python app.py` only imports the application module; it is not the server command.

## Test and quality checks

Run the standard-library regression suite with:

```bash
python -m unittest discover -s tests -v
```

The tests cover dataset cleaning, canonical pricing, recommendation data contracts, cart totals, search encoding, and order validation. For a production deployment, configure the same environment variables in the hosting service and ensure Firebase rules prevent one authenticated UID from reading another UID’s data.

## Main routes

| Route | Purpose |
|---|---|
| `/` | Guest catalog, cold-start recommendations, and search |
| `/login` | Firebase login |
| `/signup` | Firebase registration |
| `/product/<id>` | Product detail and similar products |
| `/cart` | Cart items and calculated totals |
| `/checkout` | Validated shipping details |
| `/payment` | Explicit local demo payment |
| `/orders` | Per-user order history |
| `/wishlist` | Per-user saved products |

## Contribution workflow

Create a focused branch for each maintainer-approved issue, add a regression test, and run the test suite before opening a pull request. In the pull-request description, include `Fixes #<issue-number>`, the exact behavior changed, and the verification command. Keep unrelated features in separate pull requests so the review history remains clear.

# Social Video Audience Sentiment Intelligence

A machine-learning-powered system that instantly analyzes thousands of YouTube comments to determine whether the audience sentiment is **Positive** or **Negative**.

The system pulls comments live from the YouTube Data API, trains a LightGBM model, and serves it through a Flask API that a custom Chrome extension calls to show an "overall vibe" for any video.

> Full design rationale (inspiration, approach, and why each technology was chosen) is in [`docs/PROJECT_DOCUMENTATION.md`](docs/PROJECT_DOCUMENTATION.md).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Model | LightGBM (Gradient Boosting) + TF-IDF Vectorization |
| Labeling | VADER (NLTK) |
| Backend | Python Flask API |
| Frontend | Custom Chrome Extension (JavaScript) |
| Ops | Dockerized & Deployed on Cloud (Render) |
| Tracking | MLflow for experiment management |
| Data Source | YouTube Data API v3 |

---

## Project Structure

```
Social-Video-Audience-Sentiment-Intelligence/
├── app.py                    # Flask API (serves the trained model)
├── pipeline_run.py           # Runs the full pipeline (ingest → transform → train)
├── requirements.txt          # Python dependencies
├── setup.py                  # Package metadata
├── Dockerfile                # Containerizes the Flask app
├── .env                      # Your YouTube API key (create this)
├── src/
│   ├── logger.py             # Logging setup
│   ├── exception.py          # Custom exception handling
│   ├── utils.py              # Pickle save helper
│   └── components/
│       ├── data_ingestion.py       # Fetches comments from YouTube API
│       ├── data_transformation.py  # Cleans text, VADER labeling, TF-IDF
│       └── model_trainer.py        # Trains LightGBM, logs to MLflow
├── artifacts/                # Trained model, preprocessor, raw data
├── extension/                # Chrome extension (popup + manifest)
├── mlruns/ + mlflow.db       # MLflow experiment tracking
└── docs/
    └── PROJECT_DOCUMENTATION.md
```

---

## Prerequisites

- **Python 3.9+** (tested on 3.12)
- **pip**
- A **YouTube Data API v3 key** — get one free from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials). Enable the "YouTube Data API v3" for your project first.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Abhishekhash101/Social-Video-Audience-Sentiment-Intelligence.git
cd Social-Video-Audience-Sentiment-Intelligence
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set up your API key

Create a `.env` file in the project root and add your YouTube API key:

```bash
YOUTUBE_API=YOUR_YOUTUBE_API_KEY
```

> The `.env` file is git-ignored, so your key stays private.

---

## Running the Project

### Option A — Run the Flask API (uses the already-trained model)

The trained model and preprocessor are already saved in `artifacts/`, so you can serve the API immediately:

```bash
python app.py
```

The server starts on **http://localhost:7860**.

**Test it:**

```bash
# Health check
curl http://localhost:7860/

# Predict sentiment
curl -X POST http://localhost:7860/predict \
  -H "Content-Type: application/json" \
  -d '{"comment": "This video is amazing and I love it!"}'
```

Expected response:

```json
{
  "comment": "This video is amazing and I love it!",
  "prediction_code": 1,
  "sentiment": "Positive"
}
```

### Option B — Re-run the full pipeline (retrain the model)

This fetches fresh comments, transforms them, and retrains the model. Requires a valid `YOUTUBE_API` key in `.env`.

```bash
python pipeline_run.py
```

> **Note:** `pipeline_run.py` currently has a bug — it uses `os.getenv('YOUTUBE_API')` without importing `os`, which raises a `NameError`. Add `import os` at the top of the file to fix it before running.

---

## Using the Chrome Extension

1. Open `chrome://extensions` in Chrome.
2. Enable **Developer mode** (toggle in the top-right).
3. Click **Load unpacked** and select the `extension/` folder.
4. Open any YouTube video and scroll down to load comments.
5. Click the extension icon, then **Analyze Comments**.

> **Note:** `extension/popup.js` currently points to the deployed API at `https://social-video-audience-sentiment.onrender.com/predict`. To test against your local server, change that URL to `http://localhost:7860/predict`.

---

## Running with Docker

```bash
# Build the image
docker build -t sentiment-api .

# Run the container
docker run -p 7860:7860 sentiment-api
```

The API will be available at **http://localhost:7860**.

---

## MLflow Experiment Tracking

Training runs are logged to MLflow. To view the experiment dashboard:

```bash
mlflow ui
```

Then open **http://localhost:5000** in your browser to see logged parameters, metrics, and models.

---

## Deployment

The app is Dockerized and can be deployed to any cloud platform. It is currently deployed on **Render** at:

```
https://social-video-audience-sentiment.onrender.com
```

---

## License

This project is for educational purposes. Built as a challenge to reconstruct a production-grade ML system from an architecture blueprint.

# Social Video Audience Sentiment Intelligence — Project Documentation

## 1. Overview

**Social Video Audience Sentiment Intelligence** is a machine-learning-powered system that instantly analyzes thousands of YouTube comments to determine whether the audience sentiment is **Positive** or **Negative**.

It is a full-cycle MLOps project: data is pulled live from the YouTube Data API, cleaned and labeled, a model is trained and tracked, and the trained model is served through a Flask API that a custom Chrome extension calls to show an "overall vibe" for any video.

---

## 2. The Inspiration

> *"A huge shoutout to Krish Naik. While I didn't take his specific 'Real-World Projects' course, I stumbled upon his course curriculum and Software Architecture diagram. I took that as a challenge: 'Can I build this entire production-grade system just by looking at the architecture?' The answer is YES. Thank you, Krish, for providing such high-quality blueprints that push developers to build real things."*

The project was born from a deliberate challenge. Rather than following a step-by-step tutorial, the goal was to take a **high-level software architecture blueprint** and independently reconstruct a complete, production-grade ML system from it. This forced a deep understanding of every layer — data ingestion, transformation, model training, experiment tracking, serving, and deployment — instead of just copying code.

The result is a system that demonstrates the **entire ML lifecycle**, not just a notebook with a model.

---

## 3. The Approach

The system is built as a modular, end-to-end pipeline. Each stage is a separate component under `src/components/`, which keeps the code clean, testable, and replaceable.

### 3.1 Data Ingestion — `data_ingestion.py`
- Connects to the **YouTube Data API v3** using a developer key.
- Fetches comment threads for a given video ID, paginating through results (100 per request).
- Extracts `author`, `comment`, `date`, and `like_count` for each comment.
- Saves the raw comments to `artifacts/raw_data.csv`.

### 3.2 Data Transformation — `data_transformation.py`
- **Cleaning:** removes non-alphabetic characters, lowercases, tokenizes, removes English stopwords (keeping `not` so negation is preserved), and applies Porter stemming.
- **Pseudo-labeling:** since YouTube comments have no ground-truth sentiment labels, the **VADER** sentiment analyzer is used to auto-generate labels (`1` for positive compound score, `0` otherwise).
- **Vectorization:** converts cleaned text into numerical features using **TF-IDF** (max 5000 features).
- **Splitting:** 80/20 train/test split.
- Saves the fitted TF-IDF vectorizer to `artifacts/preprocessor.pkl`.

### 3.3 Model Training — `model_trainer.py`
- Trains a **LightGBM** gradient-boosting classifier.
- Logs parameters, metrics (accuracy, precision, recall, F1), and the model itself to **MLflow**.
- Saves the trained model to `artifacts/model.pkl` for the Flask app to load.

### 3.4 Serving — `app.py`
- A **Flask** API with CORS enabled.
- `GET /` — health check.
- `POST /predict` — accepts a comment, cleans it, vectorizes it with the saved preprocessor, predicts sentiment, and returns `Positive`/`Negative`.

### 3.5 Frontend — `extension/`
- A **Chrome Extension (Manifest V3)** that scrapes visible comments from the YouTube page DOM and sends them to the `/predict` API.
- Aggregates the results and displays the percentage of positive vs. negative sentiment.

### 3.6 Ops & Deployment
- **Dockerized** via `Dockerfile` (Python 3.9-slim, installs `libgomp1` for LightGBM).
- **Deployed** to the cloud on **Render**.
- **Experiment tracking** with **MLflow** (`mlruns/` + `mlflow.db`).

---

## 4. Why We Chose This Approach

### 4.1 Why LightGBM for model training?

- **Speed & Scalability:** LightGBM uses **Gradient-based One-Side Sampling (GOSS)** and **Exclusive Feature Bundling (EFB)**, making it significantly faster to train than traditional gradient boosting (like XGBoost) — important when processing thousands of comments.
- **High Accuracy on Tabular/Text-Feature Data:** It consistently delivers state-of-the-art results on structured data, which is exactly what TF-IDF produces (a sparse numeric matrix).
- **Low Memory Footprint:** Histogram-based learning keeps memory usage low, so the model is lightweight enough to serve in a small cloud container.
- **Handles Sparse Data Well:** TF-IDF matrices are highly sparse; LightGBM handles sparse inputs efficiently.
- **Good Defaults:** With `n_estimators=100` and `learning_rate=0.05`, it gives strong baseline performance without heavy tuning.

### 4.2 Why TF-IDF for text vectorization?

- **Simple and Effective:** Unlike deep embeddings, TF-IDF is lightweight, interpretable, and requires no GPU or large pretrained models.
- **Captures Word Importance:** It weights words by how distinctive they are to a document, which works well for short, informal text like comments.
- **Fast to Train and Serve:** Fits the "production-grade but lightweight" goal of the project.

### 4.3 Why VADER for pseudo-labeling?

- **Built for Social Media Text:** VADER is specifically tuned for short, informal, emoji-heavy text — exactly what YouTube comments are.
- **No Training Data Required:** It is a rule-based lexicon model, so we can generate labels instantly without a labeled dataset.
- **Good Enough for Bootstrapping:** It provides a reasonable proxy for ground truth, enabling a supervised model to be trained end-to-end.

### 4.4 Why Flask for the backend?

- **Lightweight & Simple:** Perfect for a single-purpose prediction API.
- **Easy CORS Support:** `flask-cors` makes it trivial to call the API from a browser extension.
- **Quick to Deploy:** Works cleanly with Docker and Render.

### 4.5 Why a Chrome Extension for the frontend?

- **Native Context:** It runs directly on the YouTube page, so it can scrape comments from the DOM without any server-side scraping.
- **Zero Backend Scraping Cost:** No need to pay for or maintain a scraping service.
- **Instant UX:** Users click one button and get an immediate sentiment breakdown.

### 4.6 Why MLflow?

- **Experiment Tracking:** Logs metrics and parameters so every training run is reproducible and comparable.
- **Model Registry:** Stores model artifacts in a structured way (`mlruns/`), making it easy to version and retrieve models.
- **Industry Standard:** Demonstrates real MLOps practice, not just model building.

### 4.7 Why Docker + Render?

- **Docker** ensures the app runs identically anywhere (local, cloud) by packaging the runtime, dependencies, and system libraries (`libgomp1` for LightGBM).
- **Render** provides free, simple cloud hosting with automatic HTTPS, so the extension can call the API from any browser.

---

## 5. Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Brain (Model) | LightGBM (Gradient Boosting) + TF-IDF Vectorization |
| Labeling | VADER (NLTK) |
| Backend | Python Flask API |
| Frontend | Custom Chrome Extension (JavaScript) |
| Ops | Dockerized & Deployed on Cloud (Render) |
| Tracking | MLflow for experiment management |
| Data Source | YouTube Data API v3 |

---

## 6. Key Takeaway

This project proves that a **production-grade ML system can be built from an architecture blueprint alone**. Every choice — from LightGBM to TF-IDF to VADER to Flask to a Chrome extension — was made to balance **accuracy, speed, simplicity, and real-world deployability**, resulting in a complete, working MLOps pipeline rather than just a model in a notebook.

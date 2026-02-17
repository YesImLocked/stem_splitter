# Stem Splitter

Separate any song into **vocals, drums, bass & other** — powered by [Demucs](https://github.com/facebookresearch/demucs).

Live demo: **[yesimlocked.github.io/stem_splitter](https://yesimlocked.github.io/stem_splitter)**

---

## Deployment

### 1 — Deploy the backend to Render (free)

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New → Web Service** and select this repository.
3. Render will auto-detect `render.yaml` and configure everything.
4. Click **Deploy**. Copy the URL once it's live (e.g. `https://stem-splitter.onrender.com`).

### 2 — Point the frontend to your backend

Edit `docs/index.html` and update line:

```js
const API_URL = 'https://stem-splitter.onrender.com';
```

Replace it with your actual Render URL.

### 3 — Enable GitHub Pages

1. Push your changes to `main`.
2. Go to **Settings → Pages** in your GitHub repo.
3. Set **Source** to `Deploy from a branch`, branch `main`, folder `/docs`.
4. Click **Save**. Your site will be live at `https://yesimlocked.github.io/stem_splitter/`.

---

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>.

## Stack

- **Backend**: Python · Flask · Demucs (htdemucs model)
- **Frontend**: Vanilla HTML/CSS/JS (no build step)
- **Hosting**: Render (backend) + GitHub Pages (frontend)

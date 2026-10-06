# Vòng chung khảo

Thư mục nộp bài / làm việc cho đội **GenAI Nexus** (`AITC-418`).

## Hướng dẫn

- Đặt toàn bộ source, tài liệu, demo liên quan **Vòng chung khảo** trong thư mục `chung-khao/` này.
- Có thể tạo nhánh riêng theo quy ước đội, nhưng **nội dung vòng này** phải nằm dưới `chung-khao/`.
- Không đẩy secret (API key, `.env`, password) lên repo.

```
chung-khao/
├── README.md          ← file này
└── (code của đội)
```

## Run the itinerary workflow

From the repository root, create a virtual environment and install the round dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r chung-khao/requirements.txt
```

Copy `chung-khao/.env.example` to `chung-khao/.env` and set `THUCCHIEN_API_KEY`. The itinerary agent uses `gpt-6-luna` through the organizer gateway by default. The key stays in the API process and must not be committed.

Start the API in one terminal, from the repository root:

```bash
cd chung-khao
uvicorn api:app --host 127.0.0.1 --port 8000
```

Start the web app in a second terminal, from the repository root:

```bash
source .venv/bin/activate
python3 -m streamlit run chung-khao/app.py
```

Open `http://localhost:8501`, choose **Lên lịch trình**, enter preferences, generate, review, revise, and optionally save. `http://127.0.0.1:8000/health` returns API health. Prices, places, routes, and opening hours are unverified AI suggestions; confirm them before booking.

Saving is optional. To enable it, run [agent/supabase.sql](agent/supabase.sql) in Supabase, then set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `chung-khao/.env`. Without those settings, Save returns a clear unavailable message. Set `ITINERARY_API_URL` when the API is hosted separately from the web app. Keep the API private or add authentication before exposing Save publicly; the initial architecture has no user accounts.

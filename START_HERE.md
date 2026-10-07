# Start Here

## 1. Add the dataset

Put your Kaggle CSV at:

`data/ecommerce_sales.csv`

## 2. Start the backend

Open Terminal 1:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://localhost:8000
API docs: http://localhost:8000/docs

## 3. Start the React frontend

Open Terminal 2 from the project root:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

The browser should show the full-stack dashboard.

## Optional AI mode

Without an API key, the AI Analyst runs in safe demo SQL mode for common questions.
To enable LLM text-to-SQL, export an OpenAI API key before starting the backend:

```bash
export OPENAI_API_KEY="your-key"
```

Never commit an API key to GitHub.

## Optional Docker version

If Docker Desktop is installed:

```bash
docker compose up --build
```

Then open http://localhost:3000

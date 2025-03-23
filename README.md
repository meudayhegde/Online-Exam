# A tech Platform to conduct an Online Exam

## Pre-Requirements
[Python](https://www.python.org/downloads/)
[NextJS](https://nextjs.org/docs/app/getting-started/installation)

## Setup
`git clone https://github.com/meudayhegde/Online-Exam.git`

---
## [frontend](https://github.com/meudayhegde/Online-Exam/tree/main/frontend)
## Frontend for Online Exam Platform (Next.js - [Docs](https://nextjs.org/docs), [Resources]())
### Setup

```
cd frontend
npm i
npm run dev
```

### Pages
#### Login Page
- http://127.0.0.1:3000/login -> src/app/login
    - [page.js](https://github.com/meudayhegde/Online-Exam/blob/main/frontend/src/app/login/page.js)
    - Other files - components used in login page

#### Exam page
- http://127.0.0.1:3000/exam -> src/app/login
    - [page.js](https://github.com/meudayhegde/Online-Exam/blob/main/frontend/src/app/exam/page.js)
    - other files - components used in Exam page

### Complete
### Unauthorized
### Admin


---
## [backend](https://github.com/meudayhegde/Online-Exam/tree/main/backend)
## APIs for Online Exam Platform (FastAPI [Docs](https://fastapi.tiangolo.com/), [Resources]())

### Setup
edit `backend/.env` file, and include `MONGO_CONNECTION_URI` for mongo DB connection.

```
cd backend
python3 -m pip install -r requirements.txt
python3 app.py
```

API Source code -> [app.py](https://github.com/meudayhegde/Online-Exam/tree/main/backend)
API Docs -> [OpenAPI Docs](http://127.0.0.1:8000/docs)

### Background tasks
[evaluate_submission](https://github.com/meudayhegde/Online-Exam/blob/6f1b1ea7bde7d05751e1527837218015895fa819/backend/app.py#L137)

[calculate_rank_and_percentile](https://github.com/meudayhegde/Online-Exam/blob/6f1b1ea7bde7d05751e1527837218015895fa819/backend/app.py#L171C11-L171C40)

[calculate_rank_and_percentile_with_pipeline](https://github.com/meudayhegde/Online-Exam/blob/6f1b1ea7bde7d05751e1527837218015895fa819/backend/app.py#L212)


### API Content definitions
[models.py](https://github.com/meudayhegde/Online-Exam/blob/main/backend/models.py)

### Testing with 10000 users
[test](https://github.com/meudayhegde/Online-Exam/blob/main/backend/test.py)

#### Steps
    - Add MONGO_CONNECTION_URI
    - Start API Server, `python app.py`
    - terminal new tab -> run test, `python test.py`

    - For Calculating Ranking, Evaluation, `POST` http://127.0.0.1:8000/api/calculate-results?exam_code=CAT2025
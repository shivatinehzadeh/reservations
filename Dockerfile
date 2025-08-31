FROM python:3.13.3 AS base
WORKDIR /reservations

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000


FROM base AS test
CMD ["pytest", "-vv"]


FROM base AS production
CMD ["bash", "-c", "python create_table.py && uvicorn setup.base:app --host 0.0.0.0 --port 8000"]

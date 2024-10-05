FROM python:3.12

RUN pip install "poetry==1.8.3"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install

COPY ./ /app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "lecture_2.hw.shop_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
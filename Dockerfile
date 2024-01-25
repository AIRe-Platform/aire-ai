FROM python:3.11-slim
WORKDIR ./

COPY ./requirements.txt ./
COPY ./app ./app

RUN pip install -r requirements.txt

CMD cd app; exec uvicorn server:app --host 0.0.0.0 --port 80

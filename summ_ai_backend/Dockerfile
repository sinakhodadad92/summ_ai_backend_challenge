FROM python:3.10
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOME=/home/summ_ai_backend

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y \
    && apt-get clean

COPY ./requirements.txt ./requirements.txt
COPY ./entrypoint.sh ./entrypoint.sh

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=summ_ai_backend.settings

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "./entrypoint.sh"]
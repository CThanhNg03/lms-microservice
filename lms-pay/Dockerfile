FROM python:3.10-bullseye

# # Install OpenSSL and other dependencies
# RUN apt-get update && apt-get install -y \
#     libssl-dev \
#     libffi-dev \
#     libbz2-dev \
#     libreadline-dev \
#     libsqlite3-dev \
#     libncurses5-dev \
#     libgdbm-dev \
#     zlib1g-dev \
#     liblzma-dev \
#     build-essential \
#     wget \
#     curl \
#     && apt-get clean

# # Install Python dependencies
# RUN pip install --upgrade pip setuptools

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install -r requirements.txt

COPY /.env /code/.env

COPY /app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
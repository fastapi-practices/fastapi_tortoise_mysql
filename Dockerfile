FROM python:3.10-slim

WORKDIR /ftm

COPY . .

RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
    && sed -i s@/security.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple \
    && pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

ENV TZ = Asia/Shanghai

RUN mkdir -p /var/log/fastapi_server

EXPOSE 8001

CMD ["uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]

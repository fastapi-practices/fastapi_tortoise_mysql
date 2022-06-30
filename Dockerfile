FROM python:3.8-slim as builder

WORKDIR /build

COPY requirements.txt /build/requirements.txt

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --no-cache-dir -r /build/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

FROM python:3.8-slim

WORKDIR /ftmp

ENV TZ = Asia/Shanghai

COPY ./backend /ftmp/backend

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"]

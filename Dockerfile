FROM python:3.7-slim
RUN mkdir /app
COPY requirements.txt /app
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY yatube/ /app
WORKDIR /app
CMD ["gunicorn", "yatube.wsgi:application", "--bind", "0:8000" ]
FROM python:3.11
COPY . .
RUN pip install -r requirements.txt
WORKDIR /src

CMD [ "python", "main.py" ]
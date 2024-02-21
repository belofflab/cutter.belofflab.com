FROM python:3.10

WORKDIR /opt/bot

COPY requirements.txt .

RUN python3 -m pip install virtualenv 
RUN python3 -m virtualenv /opt/bot/venv

RUN /opt/bot/venv/bin/pip install -r requirements.txt

COPY . .

CMD ["/opt/bot/venv/bin/python", "bot.py"]


EXPOSE 6699
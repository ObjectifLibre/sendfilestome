FROM python:3.6

RUN apt update && apt install -y libldap2-dev libsasl2-dev && rm -rf /var/lib/apt/lists/*
RUN adduser --disabled-password --gecos '' app
RUN mkdir -p /sendfilestome/uploads
WORKDIR /sendfilestome
COPY entrypoint.sh manage.py requirements.txt ./
ADD sendfilestome /sendfilestome/sendfilestome
RUN cp /sendfilestome/sendfilestome/settings.py.example /sendfilestome/sendfilestome/settings.py && \
    chown -R app /sendfilestome && \
    pip install -r requirements.txt

USER app
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]

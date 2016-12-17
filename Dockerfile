FROM python:3.5.2-onbuild
COPY . /usr/src/app
WORKDIR /usr/src/app
ENTRYPOINT ["./entrypoint.sh"]

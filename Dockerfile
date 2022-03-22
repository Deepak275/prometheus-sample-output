FROM python:3.8-alpine
COPY . /
RUN pip install -r /requirements.txt
EXPOSE 80
WORKDIR /
ENTRYPOINT ["python"]
CMD ["/app.py"]

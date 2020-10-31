FROM continuumio/anaconda3:2020.07
WORKDIR /app
COPY . /app
RUN apt-get install -y poppler-utils
RUN pip install -r requirements.txt
EXPOSE 28411
CMD ["python", "main.py"]

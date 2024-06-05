FROM python:3.10-slim
WORKDIR /goodmodelbadrequests
COPY requirements.txt .
ADD . /goodmodelbadrequests
RUN apt-get update && \
    apt-get install -y build-essential pkg-config libhdf5-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install plotly
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]

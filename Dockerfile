FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

RUN echo '#!/bin/bash\nuvicorn api.main:app --host 0.0.0.0 --port 8000 &\nstreamlit run dashboard/app.py --server.port 7860 --server.address 0.0.0.0' > /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
FROM python:3
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY app.py /usr/src/app/
COPY templates/index.html /usr/src/app/templates/
COPY static/images/load-balancer-icon.png /usr/src/app/static/images/load-balancer-icon.png
COPY static/styles/normalize.css /usr/src/app/static/styles/normalize.css
COPY static/styles/skeleton-dark.css /usr/src/app/static/styles/skeleton-dark.css

ENV HOSTNAME=${HOSTNAME}
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8882

CMD ["python", "/usr/src/app/app.py"]
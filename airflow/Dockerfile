# Use the official Python 3.11.6 image as the base
FROM python:3.11.6

# Label for Dockerfile maintenance information
LABEL maintainer="Sergio Sánchez Sánchez"

# Set the timezone to Europe/Madrid
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Apache Airflow and its dependencies
RUN pip install apache-airflow[crypto,celery,postgres,jdbc,ssh]==2.7.1

# Create an Airflow user
ENV AIRFLOW_USER_HOME=/usr/local/airflow
RUN useradd -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow

# Give the "airflow" user sudo access
RUN echo "airflow ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Copy necessary files to the container
WORKDIR ${AIRFLOW_USER_HOME}
COPY ./packages/requirements.txt packages/requirements.txt
COPY ./script/entrypoint.sh entrypoint.sh
COPY ./config/airflow.cfg airflow.cfg

# Install dos2unix to remove carriage return characters
# Install ncat (an alternative to netcat), curl, libsndfile1
RUN apt-get update && apt-get install -y ncat curl dos2unix libsndfile1

RUN pip install --upgrade pip
# Install additional Python dependencies
RUN pip install --no-cache-dir -r ./packages/requirements.txt

# Install all local packages
RUN if [ -d "/packages/local" ]; then \
        # Instalar todos los paquetes locales
        for package in /packages/local/*; do \
            pip install -e $package; \
        done; \
    fi

# Run dos2unix on script files to remove carriage return characters
RUN dos2unix entrypoint.sh
# Change permissions
RUN chmod +x entrypoint.sh
RUN chown -R airflow: ${AIRFLOW_USER_HOME}

# Expose ports
EXPOSE 8080 5555 8793

# Switch to the Airflow user and configure the entry point
USER airflow
ENTRYPOINT ["./entrypoint.sh"]
CMD ["webserver"]

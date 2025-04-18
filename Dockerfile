FROM apache/airflow:2.9.1-python3.12

COPY requirements.txt /opt/airflow/
USER root
RUN apt-get update && apt-get install -y gcc python3-dev
# Cài đặt OpenJDK 11 từ Adoptium Temurin
RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.22%2B7/OpenJDK11U-jdk_x64_linux_hotspot_11.0.22_7.tar.gz && \
    mkdir -p /usr/lib/jvm && \
    tar -xvf OpenJDK11U-jdk_x64_linux_hotspot_11.0.22_7.tar.gz -C /usr/lib/jvm && \
    rm OpenJDK11U-jdk_x64_linux_hotspot_11.0.22_7.tar.gz

# Thiết lập biến môi trường
ENV JAVA_HOME=/usr/lib/jvm/jdk-11.0.22+7
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

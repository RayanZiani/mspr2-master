FROM jenkins/jenkins:lts-jdk17

USER root

# Ajouter le dépôt pour Python 3.11
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-distutils \
    python3-pip \
    curl \
    unzip \
    nodejs \
    npm \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Docker CLI (binaire statique — docker.io Debian ne fournit pas toujours le client)
ARG DOCKER_VERSION=26.1.4
RUN curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz" \
    | tar xz -C /tmp \
    && mv /tmp/docker/docker /usr/local/bin/docker \
    && chmod +x /usr/local/bin/docker

# Docker Compose v2
ARG COMPOSE_VERSION=2.29.7
RUN curl -fsSL "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose \
    && mkdir -p /usr/local/lib/docker/cli-plugins \
    && ln -sf /usr/local/bin/docker-compose /usr/local/lib/docker/cli-plugins/docker-compose

RUN groupadd -f docker && usermod -aG docker jenkins

ARG SONAR_SCANNER_VERSION=6.2.1.4610
RUN curl -fsSL "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux-x64.zip" -o /tmp/sonar-scanner.zip \
    && unzip -q /tmp/sonar-scanner.zip -d /opt \
    && mv /opt/sonar-scanner-* /opt/sonar-scanner \
    && ln -sf /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner \
    && rm /tmp/sonar-scanner.zip

USER jenkins

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

ENV PATH="/opt/sonar-scanner/bin:/usr/local/bin:${PATH}"

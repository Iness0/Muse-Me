FROM python:3.10 as python-base
RUN useradd muse_me

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.2.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

# Create stage for Poetry installation
FROM python-base as poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Create a new stage from the base python image
FROM python-base as app
# Copy Poetry to app image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /home/muse_me

# Copy Dependencies
COPY poetry.lock pyproject.toml ./
RUN python -m venv venv
# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install Dependencies
RUN . venv/bin/activate && poetry install --no-interaction --no-cache --without dev
RUN venv/bin/pip install pymysql cryptography

# Copy Application
COPY app app
COPY migrations migrations
COPY main.py config.py boot.sh ./

#Additional setup
RUN chmod +x boot.sh
ENV FLASK_APP muse_me.py

#Create new user
RUN chown -R muse_me:muse_me ./
USER muse_me

# Run Application
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]

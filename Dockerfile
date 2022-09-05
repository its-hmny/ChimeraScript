FROM python:3.10

ENV PYTHONUNBUFFERED=true
# Poetry download/installation path
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
# Export Poetry path to bash $PATH variable
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set /ChimeraScript as working direcotry
WORKDIR /ChimeraScript
# Copies the project source into the container
COPY . ./

# Installs Poetry package manager
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
# With poetry, install the project dependencies
RUN poetry install --no-interaction --no-ansi -vvv
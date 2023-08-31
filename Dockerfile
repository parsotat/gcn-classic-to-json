FROM python:3.10 AS build
ENV POETRY_VIRTUALENVS_CREATE false
RUN curl -sSL https://install.python-poetry.org | python -
COPY . /src
WORKDIR /src
RUN $HOME/.local/bin/poetry install --only main

FROM python:slim
FROM python:3.10-slim
COPY --from=build /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=build /src/ /src/
COPY --from=build /usr/local/bin/gcn-monitor /usr/local/bin/
ENTRYPOINT ["gcn-monitor"]
USER nobody:nogroup

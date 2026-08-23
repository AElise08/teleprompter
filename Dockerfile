# Núcleo headless: dá pra validar Linux numa VPS sem desktop.
#   docker build -t ghost-teleprompter .
#   docker run --rm ghost-teleprompter
FROM python:3.12-slim-bookworm
WORKDIR /app
COPY scriptfmt.py teleprompter.py ./
COPY tests ./tests
CMD ["sh", "-c", "python -m unittest discover -s tests -v && python teleprompter.py --check"]

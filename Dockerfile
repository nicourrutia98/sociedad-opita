# Sociedad Opita — Dockerfile multi-stage para AWS Lambda

# Stage 1: builder (instala dependencias)
FROM public.ecr.aws/lambda/python:3.12 AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target /build/python -r requirements.txt

# Stage 2: runtime (imagen final)
FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task
COPY --from=builder /build/python ./python
COPY city_factory ./city_factory
COPY cities ./cities
COPY api ./api
COPY tests ./tests
COPY docs ./docs

# Handler principal
ENV PYTHONPATH=/var/task
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1

# Lambda handler (puerto 8080 para Lambda Web Adapter / Function URL)
CMD ["api.handler_simulate.lambda_handler"]

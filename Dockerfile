###############################################
# Builder Image
###############################################
FROM public.ecr.aws/lambda/python:3.10 as builder-base

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --target ${LAMBDA_TASK_ROOT}

###############################################
# Production Image
###############################################
FROM builder-base as production

# Copy function code
COPY config/ ${LAMBDA_TASK_ROOT}/config
COPY inews/ ${LAMBDA_TASK_ROOT}/inews
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set CMD to handler
CMD [ "lambda_function.handler" ]

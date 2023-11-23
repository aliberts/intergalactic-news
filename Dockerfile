FROM public.ecr.aws/lambda/python:3.10

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install --no-cache-dir -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# Copy function code
COPY config/ ${LAMBDA_TASK_ROOT}/config
COPY data/ ${LAMBDA_TASK_ROOT}/data
COPY inews/ ${LAMBDA_TASK_ROOT}/inews
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]

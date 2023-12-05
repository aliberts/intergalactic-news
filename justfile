set dotenv-load

export-req:
    poetry export -f requirements.txt --output requirements.txt --without-hashes

build:
    docker build --platform linux/amd64 -t inews:test .

run:
    docker run \
        --env AWS_ACCESS_KEY_ID \
        --env AWS_SECRET_ACCESS_KEY \
        --env AWS_REGION \
        --env GOOGLE_API_KEY \
        --env OPENAI_API_KEY \
        --env MAILCHIMP_API_KEY \
        -i -p 9000:8080 inews:test

brun: export-req build run

login-ecr:
    aws ecr get-login-password --region eu-west-3 | \
        docker login \
        --username AWS \
        --password-stdin 976114805627.dkr.ecr.eu-west-3.amazonaws.com

build-ecr:
    docker build --platform linux/amd64 -t inews .

tag-ecr:
    docker tag inews:latest 976114805627.dkr.ecr.eu-west-3.amazonaws.com/inews:latest

push-ecr:
    docker push 976114805627.dkr.ecr.eu-west-3.amazonaws.com/inews:latest

update-lambda: export-req login-ecr build-ecr tag-ecr push-ecr
    aws lambda update-function-code \
           --function-name inews \
           --image-uri 976114805627.dkr.ecr.eu-west-3.amazonaws.com/inews:latest

trigger event:
    curl "http://192.168.63.101:9000/2015-03-31/functions/function/invocations" \
        -d @{{event}}

tf-setup:
    cd terraform/setup && \
    terraform init && \
    terraform apply -auto-approve -var-file=backend.tfvars && \
    cd ../ && terraform init -backend-config=setup/backend.tfvars && \
    terraform workspace new prod && \
    terraform workspace new dev

tf-setup-destroy:
    cd terraform/setup && \
    terraform destroy -var-file=backend.tfvars

tf-plan tfenv:
    cd terraform && \
    terraform workspace select {{tfenv}} && \
    terraform plan -var-file=environments/{{tfenv}}.tfvars

tf-apply tfenv:
    cd terraform && \
    terraform workspace select {{tfenv}} && \
    export TF_VAR_google_api_key=$GOOGLE_API_KEY && \
    export TF_VAR_mailchimp_api_key=$MAILCHIMP_API_KEY && \
    export TF_VAR_openai_api_key=$OPENAI_API_KEY && \
    terraform apply -auto-approve -var-file=environments/{{tfenv}}.tfvars

tf-destroy tfenv:
    cd terraform && \
    terraform workspace select {{tfenv}} && \
    terraform destroy -auto-approve -var-file=environments/{{tfenv}}.tfvars

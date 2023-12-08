set dotenv-load

docker_url := ```
    docker-machine ls | awk \
    '$1 == "dev" {gsub("tcp://","",$5); split($5, a, ":"); print a[1]}'
    ```

export-req:
    poetry export -f requirements.txt --output requirements.txt --without-hashes

build:
    docker build --platform linux/amd64 -t inews .

run:
    docker run \
        --env AWS_ACCESS_KEY_ID \
        --env AWS_SECRET_ACCESS_KEY \
        --env AWS_REGION \
        --env GOOGLE_API_KEY \
        --env OPENAI_API_KEY \
        --env MAILCHIMP_API_KEY \
        -i -p 9000:8080 inews:latest

brun: export-req build run

trigger event:
    curl "http://{{docker_url}}:9000/2015-03-31/functions/function/invocations" \
        -d @{{event}}

login-ecr:
    aws ecr get-login-password --region eu-west-3 | \
        docker login \
        --username AWS \
        --password-stdin 976114805627.dkr.ecr.eu-west-3.amazonaws.com

tag-ecr tfenv:
    docker tag inews:latest 976114805627.dkr.ecr.eu-west-3.amazonaws.com/inews-{{tfenv}}:latest

push-ecr tfenv:
    docker push 976114805627.dkr.ecr.eu-west-3.amazonaws.com/inews-{{tfenv}}:latest

update-lambda tfenv: export-req login-ecr build (tag-ecr tfenv) (push-ecr tfenv)
    aws lambda update-function-code \
        --function-name inews-{{tfenv}} \
        --image-uri 976114805627.dkr.ecr.eu-west-3.amazonaws.com/inews-{{tfenv}}:latest

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

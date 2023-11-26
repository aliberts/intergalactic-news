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
        -i -p 9000:8080 inews:test

brun: export-req build run

login-ecr:
    aws ecr get-login-password --region eu-west-3 | \
        docker login --username AWS --password-stdin 976114805627.dkr.ecr.eu-west-3.amazonaws.com

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

trigger-debug:
    curl "http://192.168.63.101:9000/2015-03-31/functions/function/invocations" -d \
        '{"debug": true, "dummy_llm_requests": true, "send": false, "send_test": false, "pull_from_bucket": true, "push_to_bucket": false}'

trigger-dry-run:
    curl "http://192.168.63.101:9000/2015-03-31/functions/function/invocations" -d \
        '{"debug": true, "dummy_llm_requests": false, "send": false, "send_test": true, "pull_from_bucket": true, "push_to_bucket": false}'

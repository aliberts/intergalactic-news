set dotenv-load

export-req:
    poetry export -f requirements.txt --output requirements.txt --without-hashes

build:
    docker build --platform linux/amd64 -t docker-image:test .

run:
    docker run \
        --env AWS_ACCESS_KEY_ID \
        --env AWS_SECRET_ACCESS_KEY \
        --env AWS_REGION \
        -i -p 9000:8080 docker-image:test

brun: export-req build run

trigger:
    curl "http://192.168.63.101:9000/2015-03-31/functions/function/invocations" -d '{}'

cleanup:
    rm data/html/build/*.html
    rm data/newsletters/*.json
    rm data/stories/*.json
    rm data/summaries/*.json
    rm data/transcripts/*.json

FROM docker.io/library/alpine:latest as alpinebase
RUN apk add bash curl openssh

FROM alpinebase
ARG VERSION
ARG ARCH
RUN wget "https://releases.hashicorp.com/terraform/${VERSION}/terraform_${VERSION}_linux_${ARCH}.zip" &&\
    unzip "terraform_${VERSION}_linux_${ARCH}.zip" &&\
    mv terraform /usr/local/bin/terraform

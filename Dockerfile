FROM docker.io/library/alpine:latest
RUN apk add bash curl openssh
ARG VERSION
ARG ARCH
RUN wget "https://releases.hashicorp.com/terraform/${VERSION}/terraform_${VERSION}_linux_${ARCH}.zip"
RUN unzip "terraform_${VERSION}_linux_${ARCH}.zip"
RUN mv terraform /usr/local/bin/terraform

FROM docker.io/library/alpine@sha256:c74f1b1166784193ea6c8f9440263b9be6cae07dfe35e32a5df7a31358ac2060
RUN apk add bash curl
ARG VERSION
ARG ARCH
RUN wget "https://releases.hashicorp.com/terraform/${VERSION}/terraform_${VERSION}_linux_${ARCH}.zip"
RUN unzip "terraform_${VERSION}_linux_${ARCH}.zip"
RUN mv terraform /usr/local/bin/terraform

FROM alpine
RUN apk add python3 && \
    apk add nano && \
    apk add git && \
    apk add curl && \
    git clone https://github.com/Normal-OJ/SandboxTestingAPI.git

CMD tail -f /dev/null
EXPOSE 6666

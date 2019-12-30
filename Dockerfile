FROM alpine
RUN apk add python3 && \
    apk add nano && \
    apk add git && \
    apk add curl && \
    apk add zip && \
    pip3 install requests

CMD tail -f /dev/null
EXPOSE 6666

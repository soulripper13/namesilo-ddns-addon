ARG BUILD_FROM
FROM $BUILD_FROM

# Install python3
RUN apk add --no-cache python3

# Copy the script
COPY namesilo_ddns.py /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

FROM rabbitmq:3.7-management-alpine

COPY ./compose/local/rabbitmq/rabbitmq.config /etc/rabbitmq/
COPY ./compose/local/rabbitmq/definitions.json /etc/rabbitmq/

EXPOSE 5672 15671 15672

CMD ["rabbitmq-server"]

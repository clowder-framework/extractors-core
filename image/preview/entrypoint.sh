#!/bin/bash
set -e

# rabbitmq
if [ "$RABBITMQ_URI" == "" ]; then
    # configure RABBITMQ_URI if started using docker-compose or --link flag
    if [ -n "$RABBITMQ_PORT_5672_TCP_ADDR" ]; then
        RABBITMQ_URI="amqp://guest:guest@${RABBITMQ_PORT_5672_TCP_ADDR}:${RABBITMQ_PORT_5672_TCP_PORT}/${RABBITMQ_VHOST}"
    fi

    # configure RABBITMQ_URI if rabbitmq is up for kubernetes
    # TODO needs implementation maybe from NDS people
fi

# start server if asked
if [ "$1" = 'extractor' ]; then
    cd /home/clowder

    # start extractor
    for i in `seq 1 10`; do
        #  check to see if rabbitmq is up if started using docker-compose or --link flag
        if [ "$RABBITMQ_PORT_5672_TCP_ADDR" != "" ]; then
            if nc -z $RABBITMQ_PORT_5672_TCP_ADDR $RABBITMQ_PORT_5672_TCP_PORT ; then
                exec ./${MAIN_SCRIPT}
            fi
        fi

        # check to see if rabbitmq is up for kubernetes
        # TODO needs implementation maybe from NDS people

        # wait for a second and try again
        sleep 1
    done
    echo "Could not connect to RabbitMQ"
    exit -1
fi

exec "$@"

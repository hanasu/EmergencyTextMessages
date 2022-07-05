from argparse import ArgumentParser
from ast import Bytes
from pika import BlockingConnection, ConnectionParameters
from sys import exit as sys_exit
from os import _exit as os_exit
from decimal import Decimal
from numpy.random import normal
from time import sleep
import random


def init_parser() -> ArgumentParser:
    parser = ArgumentParser(
        usage="%(prog)s -w/--mean_wait [TIME] -e/--error [RATE]",
        description="Consume text messages of variable size up to 100 \
            characters. Waits a random period of time normally distributed \
            around a given mean before sending out the consumed message. \
            Provides configurable error rate to simulate message failures."
    )

    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 1.0.0"
    )
    parser.add_argument("-w", "--mean_wait", type=int, required=True,
                        choices=range(0, 181), metavar="[0-180]",
                        help="mean amount in seconds to randomly wait before \
                             sending")
    parser.add_argument("-e", "--error", type=Decimal, required=True,
                        metavar="decimal from [0-1] inclusive",
                        help="percentage of message sends that should result \
                             in failure")

    return parser


def is_error(rate) -> bool:
    return random.random() < rate

def test_error_range(args, parser) -> None:
    if args.error < 0 or args.error > 1:
        parser.error("Error must be a decimal value between 0 and 1 \
                     inclusive.")

def main() -> None:
    parser = init_parser()
    args = parser.parse_args()

    test_error_range(args, parser)

    # consider switching to async SelectConnection
    connection = BlockingConnection(ConnectionParameters("localhost", 5672))
    channel = connection.channel()

    channel.queue_declare(queue="emergency", durable=True)
    channel.queue_declare(queue="emergency-failures", durable=True)

    def callback(ch, method, properties, body) -> Bytes:
        # normally distributed, where loc is the mean
        # this can be between 0 and 180 seconds
        wait_time = normal(loc=args.mean_wait)

        # normalized values can sometimes be negative
        if wait_time < 0:
            wait_time = 0
        sleep(wait_time)

        if not is_error(args.error):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(" [x] Acked %r" % body)
        else:
            print(" [o] Rejected: %r" % body)
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            ch.basic_publish(exchange="", routing_key="emergency-failures",
                             body=body)

    channel.basic_consume(queue="emergency", on_message_callback=callback,
                          auto_ack=False)

    try:
        channel.start_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user!')
        try:
            sys_exit(0)
        except SystemExit:
            os_exit(0)

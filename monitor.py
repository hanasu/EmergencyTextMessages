from argparse import ArgumentParser
from datetime import datetime
from requests import session
from requests.exceptions import HTTPError
from pika import BlockingConnection, ConnectionParameters
from time import sleep
from sys import exit as sys_exit
from os import _exit as os_exit


def init_parser() -> ArgumentParser:
    parser = ArgumentParser(
        usage="%(prog)s -f/--frequency [SECONDS] -n/--username [USERNAME] \
               -w/--password [PASSWORD] -u/--hostname [HOST] -p/--server_port \
                [PORT] -a/--api_port [HTTP API PORT]",
        description="Monitor a messaging queue and report metrics about it. \
                     Accepts a modifiable update frequency rate in seconds."
    )

    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 1.0.0"
    )

    # 5-15 seconds is recommended by rabbitmq docs:
    # https://www.rabbitmq.com/monitoring.html#monitoring-frequency
    # HTTP API only updates in increments of 5 seconds regardless
    # of value chosen here for frequency of output
    parser.add_argument("-f", "--frequency", type=int, required=True,
                        help="frequency to update metrics, in seconds")
    parser.add_argument("-n", "--username", type=str, required=True,
                        help="RabbitMQ username")
    parser.add_argument('-w', '--password', type=str, required=True,
                        help="RabbitMQ password")
    parser.add_argument("-u", "--hostname", type=str,
                        default="localhost", help="RabbitMQ hostname")
    parser.add_argument("-p", "--server_port", type=int, default=5672,
                        help="RabbitMQ server port")
    parser.add_argument("-a", "--api_port", type=int, default=15672,
                        help="RabbitMQ HTTP API port")

    return parser


def main() -> None:
    start = datetime.now()

    while True:
        parser = init_parser()
        args = parser.parse_args()

        connection = BlockingConnection(
            ConnectionParameters(args.hostname, args.server_port))
        channel = connection.channel()
        channel.queue_declare(queue="emergency-failures", durable=True)

        sess = session()
        sess.auth = (args.username, args.password)

        # make this a function
        try:
            response = sess.get(
                f"http://{args.hostname}:{args.api_port}/api/queues/%2f/emergency")
            response.raise_for_status()
            resp_json = response.json()
            acked = resp_json['message_stats']['ack']
        except HTTPError as e:
            # if response does not return HTTP 200
            return "HTTP API Access Error: " + str(e)
        except KeyError:
            acked = 0

        print("Messages delivered:", acked)

        try:
            response = sess.get(
                f"http://{args.hostname}:{args.api_port}/api/queues/%2f/emergency-failures")
            response.raise_for_status()
            resp_json = response.json()
            rejected = resp_json['message_stats']['publish']
        except HTTPError as e:
            # if response does not return HTTP 200
            return "HTTP API Access Error: " + str(e)
        except KeyError:
            # if there has not been a rejected message yet, the queue will
            # not exist
            rejected = 0

        print("Failed messages:", rejected)

        now = datetime.now()
        diff = now - start
        if rejected != 0:
            print("Time per message:",
                  diff.total_seconds() / (acked + rejected))
        else:
            print("Time per message:", diff.total_seconds() / acked)
        sleep(args.frequency)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted by user!')
        try:
            sys_exit(0)
        except SystemExit:
            os_exit(0)

import random
import json
from pika import BlockingConnection, ConnectionParameters
from argparse import ArgumentParser
from string import ascii_letters, digits
from faker import Faker


def init_parser() -> ArgumentParser:
    parser = ArgumentParser(
        usage="%(prog)s -m/--messages [MESSAGES] -u/--hostname [HOST] \
                -p/--port [PORT NUMBER] -q/--queue_name [NAME]",
        description="Generate a configurable number of text messages. They \
                    will contain up to 100 random characters and are sent to \
                    random phone numbers. Defaults to 1000 messages."
    )

    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 1.0.0"
    )
    parser.add_argument("-m", "--messages", type=int, default=1000,
                        help="number of messages to generate")
    parser.add_argument("-u", "--hostname", type=str,
                        default="localhost", help="RabbitMQ hostname")
    parser.add_argument("-p", "--port", type=int, default=5672,
                        help="RabbitMQ server port")
    parser.add_argument("-q", "--queue_name", type=str, default="emergency",
                        help="name for the RabbitMQ routing_key and queue")

    return parser


def generate_message(phone) -> str:
    char_set = ascii_letters + digits
    num_chars = random.randint(1, 100)
    message = ''.join(random.choices(char_set, k=num_chars))
    data = {'message': message, 'phone': phone}
    return json.dumps(data)


def start_publishing(args, connection, channel) -> None:
    fake = Faker(local="en_US")

    try:
        for message in range(args.messages):
            channel.basic_publish(exchange="", routing_key=args.queue_name,
                                  body=generate_message(fake.phone_number()))
    finally:
        connection.close()


def main() -> None:
    parser = init_parser()
    args = parser.parse_args()

    connection = BlockingConnection(
                        ConnectionParameters(args.hostname, args.port))
    channel = connection.channel()
    channel.queue_declare(queue=args.queue_name, durable=True)

    start_publishing(args, connection, channel)

if __name__ == "__main__":
    main()

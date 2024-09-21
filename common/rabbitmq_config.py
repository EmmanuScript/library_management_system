import pika

def get_rabbitmq_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def setup_channel(exchange_name='library_exchange', exchange_type='topic'):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)
    return channel, connection

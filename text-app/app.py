from PIL import Image, ImageDraw
import pika
import os
import json
import logging

OUT_FOLDER = '/processed/text/'
NEW = '_text'
IN_FOLDER = "/appdata/static/uploads/"
EXCHANGE = 'image_exchange'

def create_text(path_file):
    pass

def callback(ch, method, properties, body):
    data = json.loads(body)
    filename = data['new_file']
    logging.warning(f"READING {filename}")
    create_text(IN_FOLDER + filename)
    logging.warning(f"ENDING {filename}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.exchange_declare(exchange=EXCHANGE, exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange=EXCHANGE, queue=queue_name)

channel.basic_consume(queue=queue_name, on_message_callback=callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    connection.close()

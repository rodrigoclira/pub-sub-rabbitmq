from PIL import Image, ImageOps
import pika
import os
import json
import logging

OUT_FOLDER = '/processed/rotate/'
NEW = '_rotate'
IN_FOLDER = "/appdata/static/uploads/"
EXCHANGE = 'image_exchange'

def create_rotate(path_file):
    pathname, filename = os.path.split(path_file)
    output_folder = pathname + OUT_FOLDER

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    original_image = Image.open(path_file)
    transposed = original_image.transpose(Image.Transpose.ROTATE_180)

    name, ext = os.path.splitext(filename)
    transposed.save(output_folder + name + NEW + ext)

def callback(ch, method, properties, body):
    data = json.loads(body)
    filename = data['new_file']
    logging.warning(f"READING {filename}")
    create_rotate(IN_FOLDER + filename)
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

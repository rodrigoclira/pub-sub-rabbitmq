import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import pika
import time
import json
from uuid import uuid4

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
EXCHANGE = 'image_exchange'

def get_json_str(timestamp, filename):
    d = {
        'timestamp': timestamp,
        'new_file': filename,
    }
    return json.dumps(d)


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/upload-img', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		if not os.path.exists(app.config['UPLOAD_FOLDER']):
			os.makedirs(app.config['UPLOAD_FOLDER'])
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		flash('Image successfully uploaded.')
		publish(filename)
		return render_template('upload.html', filename=filename)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

def publish(filename):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='fanout')
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key='',
        body=get_json_str(time.time(), filename)
    )
    connection.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0')

from flask import Flask
from datetime import datetime



app = Flask(__name__)

@app.route('/')
def hello():
	return 'Hello,Devopser!'
@app.route('/health')
def health():
	return 'OK'

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)

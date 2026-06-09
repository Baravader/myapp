from flask import Flask, jsonify
from datetime import datetime
import os
import psycopg2
import psycopg2.extras
from flask import request

app = Flask(__name__)

def connect_db():
	return psycopg2.connect(
		host=os.getenv("DB_HOST"),
		port=os.getenv("DB_PORT"),
		database=os.getenv("POSTGRES_DB"),
		user=os.getenv("POSTGRES_USER"),
		password=os.getenv("POSTGRES_PASSWORD")
	)

def init_db():
	try:
		conn = connect_db()
		cur = conn.cursor()

		cur.execute('''
		CREATE TABLE IF NOT EXISTS visits(
			id SERIAL PRIMARY KEY,
			visit_time TIMESTAMP NOT NULL,
			user_ip VARCHAR(45),
			user_agent TEXT
			)
		''')

		conn.commit()
		cur.close()
		conn.close()

		print('Таблица visits создана')
	except Exception as e:
		print(f"Ошибка при создании таблицы:{e}")

@app.route('/debug')
def debug_headers():
	return jsonify({
		'remote_addr': request.remote_addr,
		'headers': dict(request.headers),
		'method': request.method,
		'url': request.url
	})

@app.route('/')
def hello():
	try:
		conn = connect_db()
		cur = conn.cursor()

		cur.execute('''
		INSERT INTO visits (visit_time, user_ip, user_agent)
		VALUES (%s, %s, %s)
		''', (datetime.now(),request.headers.get('X-Forwarded-For'),'Flask App'))

		conn.commit()
		cur.close()
		conn.close()
		return ('Hello,Devopser!Visit logged at {}'.format(datetime.now()) +
				'<br>Your IP is {}'.format(request.headers.get('X-Forwarded-For')))
	except Exception as e:
		print(f"exception thrown:{e}")
@app.route('/health')
def health():
	print("1. Запрос /health получен")
	try:
		print("2. Пытаюсь подключиться к БД")
		conn = connect_db()
		print("3. Подключение успешно")
		cur = conn.cursor()
		cur.execute('SELECT 1')
		cur.close()
		conn.close()
		print("4. Запрос выполнен")
		return 'OK'
	except Exception as e:
		print('Not OK:{e}')
		return f'NOT OK,epta {e}<br>', 500

init_db()
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)

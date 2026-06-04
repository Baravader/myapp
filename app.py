from flask import Flask
from datetime import datetime
import psycopg2
import psycopg2.extras




app = Flask(__name__)

DB_CONFIG = {
	'host': 'localhost',
	'port': 5432,
	'database': 'myappdb',
	'user': 'myappuser',
	'password': '456'
}

def connect_db():
	return psycopg2.connect(**DB_CONFIG)

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

@app.route('/')
def hello():
	try:
		conn = connect_db()
		cur = conn.cursor()

		cur.execute('''
		INSERT INT visits (visit_time, user_ip, user_agent)
		VALUES (%s, %s, %s)
		''', (datetime.now(),'0.0.0.0','Flask App'))

		conn.commit()
		cur.close()
		conn.close()
		return 'Hello,Devopser!Visit logged at {}'.format(datetime.now())
	except Exception as e:
		print(f"exception thrown:{e}")
@app.route('/health')
def health():
	try :
		conn = connect_db()
		cur = conn.cursor()
		cur.execute('SELECT 1')
		cur.close()
		conn.close()
		return 'OK'
	except Exception as e:
		print(f"Not OK:{e}")

init_db()
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, jsonify
from datetime import datetime
import os
import psycopg2
import psycopg2.extras
from flask import request
from werkzeug import user_agent

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
		''', (datetime.now(),request.headers.get('X-Forwarded-For'),request.headers.get('User-Agent', 'Unknown')))

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

@app.route('/visits')
def show_visits():
	try:
		conn = connect_db()
		cur = conn.cursor()
		cur.execute('''
            SELECT id, visit_time, user_ip, user_agent 
            FROM visits 
            ORDER BY id DESC 
            LIMIT 100
        ''')
		visits = cur.fetchall()
		cur.close()
		conn.close()

		# Формируем HTML-страницу
		html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Visits log</title>
            <style>
                body { font-family: monospace; margin: 2rem; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .visits-count { margin-bottom: 1rem; font-size: 1.2rem; }
            </style>
        </head>
        <body>
            <h1>📊 Visit log</h1>
            <div class="visits-count">📌 Total in this table: ''' + str(len(visits)) + ''' (last 100)</div>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Time</th>
                    <th>IP Address</th>
                    <th>User Agent</th>
                </tr>
        '''

		for visit in visits:
			html += f'''
                <tr>
                    <td>{visit[0]}</td>
                    <td>{visit[1]}</td>
                    <td><code>{visit[2]}</code></td>
                    <td>{visit[3][:50]}{'...' if len(visit[3]) > 50 else ''}</td>
                </tr>
            '''

		html += '''
            </table>
            <p><a href="/">⬅ Back to home</a></p>
        </body>
        </html>
        '''

		return html
	except Exception as e:
		return f'<h1>Error</h1><p>{e}</p>', 500

init_db()
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)

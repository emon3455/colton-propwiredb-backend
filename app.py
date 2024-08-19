from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)

# Database configuration
db_user = 'dat9admin_test_user'
db_password = '8P^;O6FT4{O+'
host = '162.214.68.40'
db_name = 'dat9admin_my-test-db'


engine = create_engine(f'mysql+mysqldb://{db_user}:{db_password}@{host}/{db_name}', pool_recycle=3600)


Session = sessionmaker(bind=engine)

@app.route('/', methods=['GET'])
def home():
    return "Welcome! The server is running."

@app.route('/filter', methods=['GET'])
def filter_data():
    search_text = request.args.get('search_text')
    if not search_text:
        return jsonify({"error": "search_text parameter is required"}), 400

    session = Session()
    try:
        sql = text("""
        SELECT * FROM properties
        WHERE JSON_UNQUOTE(JSON_EXTRACT(address, '$.zip')) LIKE :search_text
        OR JSON_UNQUOTE(JSON_EXTRACT(address, '$.address')) LIKE :search_text
        """)
        params = {"search_text": f"%{search_text}%"}

        result_proxy = session.execute(sql, params)
        results = result_proxy.fetchall()

        if results:
            columns = result_proxy.keys()
            results_list = [dict(zip(columns, row)) for row in results]
            return jsonify(results_list)
        else:
            return jsonify({"message": "No matching records found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)

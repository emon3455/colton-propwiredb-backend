from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def connect_to_database():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='propwiredb'
    )

@app.route('/filter', methods=['GET'])
def filter_data():
    search_text = request.args.get('search_text')
    if not search_text:
        return jsonify({"error": "search_text parameter is required"}), 400

    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        sql = """
        SELECT * FROM properties
        WHERE JSON_UNQUOTE(JSON_EXTRACT(address, '$.zip')) LIKE %s
        OR JSON_UNQUOTE(JSON_EXTRACT(address, '$.address')) LIKE %s
        """
        params = (f"%{search_text}%", f"%{search_text}%")

        cursor.execute(sql, params)
        results = cursor.fetchall()

        if results:
            columns = [desc[0] for desc in cursor.description]
            results_list = [dict(zip(columns, row)) for row in results]
            return jsonify(results_list)
        else:
            return jsonify({"message": "No matching records found."}), 404

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)

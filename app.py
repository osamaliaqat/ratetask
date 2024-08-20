import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        return conn
    except psycopg2.OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        raise


def get_ports_in_region(region_slug, conn):
    try:
        with conn.cursor() as cur:
            query = """
                WITH RECURSIVE region_tree AS (
                    SELECT slug FROM regions WHERE slug = %s
                    UNION ALL
                    SELECT r.slug FROM regions r
                    INNER JOIN region_tree rt ON r.parent_slug = rt.slug
                )
                SELECT code FROM ports WHERE parent_slug IN (SELECT slug FROM region_tree);
            """
            cur.execute(query, (region_slug,))
            ports = cur.fetchall()
        return [p[0] for p in ports]
    except psycopg2.Error as e:
        app.logger.error(f"Database query error: {e}")
        raise


def validate_date(date_str):
    """Validates Date Format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@app.route("/rates", methods=["GET"])
def get_average_prices():
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    origin = request.args.get("origin")
    destination = request.args.get("destination")

    if not date_from or not date_to or not origin or not destination:
        return jsonify({"error": "Missing required parameters"}), 400

    if not validate_date(date_from) or not validate_date(date_to):
        return jsonify({"error": "Invalid date format"}), 400

    try:
        conn = get_db_connection()

        origin_ports = (
            get_ports_in_region(origin, conn) if len(origin) > 5 else [origin]
        )
        destination_ports = (
            get_ports_in_region(destination, conn)
            if len(destination) > 5
            else [destination]
        )

        with conn.cursor() as cur:
            query = """
                SELECT
                    day,
                    AVG(price) AS average_price,
                    COUNT(price) AS price_count
                FROM prices
                WHERE orig_code = ANY(%s)
                AND dest_code = ANY(%s)
                AND day BETWEEN %s AND %s
                GROUP BY day
                HAVING COUNT(price) >= 3;
            """
            cur.execute(query, (origin_ports, destination_ports, date_from, date_to))
            results = cur.fetchall()

        response = []
        for day in results:
            response.append(
                {
                    "day": day[0].strftime("%Y-%m-%d"),
                    "average_price": int(day[1]) if day[2] >= 3 else None,
                }
            )

        conn.close()
        return jsonify(response)

    except psycopg2.Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)

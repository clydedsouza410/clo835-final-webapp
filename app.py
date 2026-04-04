from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import logging
from botocore.exceptions import ClientError

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", "3306"))

APP_AUTHOR = os.environ.get("APP_AUTHOR", "Your Name")
BG_IMAGE_BUCKET = os.environ.get("BG_IMAGE_BUCKET", "")
BG_IMAGE_KEY = os.environ.get("BG_IMAGE_KEY", "")
BG_IMAGE_LOCAL_DIR = os.environ.get("BG_IMAGE_LOCAL_DIR", "static/images")
BG_IMAGE_LOCAL_NAME = os.environ.get("BG_IMAGE_LOCAL_NAME", "background.png")

LOCAL_IMAGE_PATH = f"{BG_IMAGE_LOCAL_DIR}/{BG_IMAGE_LOCAL_NAME}"


def get_db_connection():
    try:
        return connections.Connection(
            host=DBHOST,
            port=DBPORT,
            user=DBUSER,
            password=DBPWD,
            db=DATABASE
        )
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None


def download_background_image():
    if not BG_IMAGE_BUCKET or not BG_IMAGE_KEY:
        logging.warning("S3 background image settings are missing.")
        return None

    os.makedirs(BG_IMAGE_LOCAL_DIR, exist_ok=True)

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        )

        s3.download_file(BG_IMAGE_BUCKET, BG_IMAGE_KEY, LOCAL_IMAGE_PATH)
        logging.info(f"Background image URL: s3://{BG_IMAGE_BUCKET}/{BG_IMAGE_KEY}")
        return "/" + LOCAL_IMAGE_PATH

    except ClientError as e:
        logging.error(f"Failed to download image from S3: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error downloading image: {e}")
        return None


@app.route("/", methods=["GET", "POST"])
def home():
    bg_image = download_background_image()
    return render_template("addemp.html", bg_image=bg_image, app_author=APP_AUTHOR)


@app.route("/about", methods=["GET", "POST"])
def about():
    bg_image = download_background_image()
    return render_template("about.html", bg_image=bg_image, app_author=APP_AUTHOR)


@app.route("/addemp", methods=["POST"])
def add_emp():
    emp_id = request.form["emp_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    primary_skill = request.form["primary_skill"]
    location = request.form["location"]

    db_conn = get_db_connection()
    bg_image = download_background_image()

    if db_conn is None:
        return render_template(
            "addempoutput.html",
            name="Database unavailable",
            bg_image=bg_image,
            app_author=APP_AUTHOR
        )

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name
    except Exception as e:
        logging.error(f"Insert failed: {e}")
        emp_name = "Database unavailable"
    finally:
        cursor.close()
        db_conn.close()

    return render_template("addempoutput.html", name=emp_name, bg_image=bg_image, app_author=APP_AUTHOR)


@app.route("/getemp", methods=["GET", "POST"])
def get_emp():
    bg_image = download_background_image()
    return render_template("getemp.html", bg_image=bg_image, app_author=APP_AUTHOR)


@app.route("/fetchdata", methods=["GET", "POST"])
def fetch_data():
    emp_id = request.form["emp_id"]
    bg_image = download_background_image()
    db_conn = get_db_connection()

    if db_conn is None:
        return render_template(
            "getempoutput.html",
            id="N/A",
            fname="Database",
            lname="Unavailable",
            interest="N/A",
            location="N/A",
            bg_image=bg_image,
            app_author=APP_AUTHOR
        )

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        if result is None:
            return render_template(
                "getempoutput.html",
                id=emp_id,
                fname="Not",
                lname="Found",
                interest="N/A",
                location="N/A",
                bg_image=bg_image,
                app_author=APP_AUTHOR
            )

        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]

    except Exception as e:
        logging.error(f"Fetch failed: {e}")
        return render_template(
            "getempoutput.html",
            id=emp_id,
            fname="Database",
            lname="Unavailable",
            interest="N/A",
            location="N/A",
            bg_image=bg_image,
            app_author=APP_AUTHOR
        )
    finally:
        cursor.close()
        db_conn.close()

    return render_template(
        "getempoutput.html",
        id=output["emp_id"],
        fname=output["first_name"],
        lname=output["last_name"],
        interest=output["primary_skills"],
        location=output["location"],
        bg_image=bg_image,
        app_author=APP_AUTHOR
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)

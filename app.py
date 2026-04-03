from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import logging
from botocore.exceptions import ClientError

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# DB config from environment
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", "3306"))

# App config from environment
APP_AUTHOR = os.environ.get("APP_AUTHOR", "Your Name")

# S3 config
BG_IMAGE_BUCKET = os.environ.get("BG_IMAGE_BUCKET", "")
BG_IMAGE_KEY = os.environ.get("BG_IMAGE_KEY", "")
BG_IMAGE_LOCAL_DIR = os.environ.get("BG_IMAGE_LOCAL_DIR", "static/images")
BG_IMAGE_LOCAL_NAME = os.environ.get("BG_IMAGE_LOCAL_NAME", "background.jpg")

LOCAL_IMAGE_PATH = f"{BG_IMAGE_LOCAL_DIR}/{BG_IMAGE_LOCAL_NAME}"


# ✅ FIX: create DB connection only when needed
def get_db_connection():
    return connections.Connection(
        host=DBHOST,
        port=DBPORT,
        user=DBUSER,
        password=DBPWD,
        db=DATABASE
    )


# S3 download function
def download_background_image():
    if not BG_IMAGE_BUCKET or not BG_IMAGE_KEY:
        logging.warning("S3 background image settings are missing.")
        return None

    os.makedirs(BG_IMAGE_LOCAL_DIR, exist_ok=True)

    s3 = boto3.client("s3")
    try:
        s3.download_file(BG_IMAGE_BUCKET, BG_IMAGE_KEY, LOCAL_IMAGE_PATH)
        logging.info(f"Background image URL: s3://{BG_IMAGE_BUCKET}/{BG_IMAGE_KEY}")
        return "/" + LOCAL_IMAGE_PATH
    except ClientError as e:
        logging.error(f"Failed to download image from S3: {e}")
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

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"

    # ✅ FIX: use fresh DB connection
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name
    finally:
        cursor.close()
        db_conn.close()

    bg_image = download_background_image()
    return render_template("addempoutput.html", name=emp_name, bg_image=bg_image, app_author=APP_AUTHOR)


@app.route("/getemp", methods=["GET", "POST"])
def get_emp():
    bg_image = download_background_image()
    return render_template("getemp.html", bg_image=bg_image, app_author=APP_AUTHOR)


@app.route("/fetchdata", methods=["GET", "POST"])
def fetch_data():
    emp_id = request.form["emp_id"]
    output = {}

    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"

    # ✅ FIX: use fresh DB connection
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            output["emp_id"] = ""
            output["first_name"] = "Not Found"
            output["last_name"] = ""
            output["primary_skills"] = ""
            output["location"] = ""
    finally:
        cursor.close()
        db_conn.close()

    bg_image = download_background_image()

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
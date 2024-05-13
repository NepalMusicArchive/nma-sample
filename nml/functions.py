import time
import os
import time
import sys
from datetime import datetime, timezone
import pytz
import requests

# from nml.config.config import *
from nml import *
from nml.functions import *
from nml.models import *
from flask_login import login_user, logout_user, current_user, login_required
from flask import render_template, url_for, redirect, flash, request, jsonify
import email
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tarfile
from pydub import AudioSegment
import hashlib


@app.before_request
def check_last_active():
    # max_idle_time=40
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first()
        last_active = current_user.last_active

        if (datetime.utcnow() - last_active).seconds > max_idle_time:
            user.login_state = 0
            db.session.commit()
            logout_user()
            flash("You have been logged out due to inactivity.", category="warning")
            # logout_user()
            return redirect(url_for("login"))
        else:
            current_user.last_active = datetime.utcnow()
            db.session.commit()


def timeline_if(input, output):
    if input:
        output = input
    else:
        output = ""
    return output


# logout function



@app.route("/get_percent/<int:total>/<int:count>",methods=["GET"])
@login_required
def get_percent(total,count):
    try:
        percentage = (count / total) * 100
        return f"{percentage:.2f}%"
    except ZeroDivisionError:
        return "Total should not be zero. Please provide a non-zero value for 'total'."


@app.route("/logout")
@login_required
def logout():
    user = User.query.filter_by(username=current_user.username).first()
    user.login_state = 0
    db.session.commit()
    flash(f"User logged out. Please login to make changes.", category="info")
    logout_user()
    return redirect(url_for("homepage"))


## check for active users
def get_nowactive_users():
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    logged_in_users = User.query.filter(
        User.last_active != None, User.login_state != False
    ).all()
    nowactive_users = []
    for users in logged_in_users:
        if (datetime.utcnow() - users.last_active).seconds < max_idle_time:
            last_active_local = users.last_active.replace(tzinfo=pytz.utc).astimezone(
                local_tz
            )
            nowactive_users.append((users, last_active_local))
    return nowactive_users


# to select the company from the DB while editing


@app.route("/get_default_company/<int:id>", methods=["GET"])
def get_default_company(id):
    contrib = (
        db.session.query(Collection.company_id).filter(Collection.id == id).first()
    )
    default_company = contrib[0]
    return default_company


# to select the contributor from the DB while editing


@app.route("/get_default_contributor/<int:id>", methods=["GET"])
def get_default_contributor(id):
    contrib = (
        db.session.query(Collection.collector_id).filter(Collection.id == id).first()
    )
    default_contributor = contrib[0]
    return default_contributor


# to select the media from the DB while editing
@app.route("/get_default_media/<int:id>", methods=["GET"])
def get_default_media(id):
    contrib = db.session.query(Collection.media_id).filter(Collection.id == id).first()
    default_media = contrib[0]
    return default_media


# to select the format from the DB while editing
@app.route("/get_default_format/<int:id>", methods=["GET"])
def get_default_format(id):
    contrib = db.session.query(Collection.format_id).filter(Collection.id == id).first()
    default_format = contrib[0]
    return default_format


# to select the language the DB while editing


@app.route("/get_default_languagem/<int:id>", methods=["GET"])
def get_default_languagem(id):
    mnth = db.session.query(Collection.language_id).filter(Collection.id == id).first()
    default_language = mnth[0]
    return default_language


# to select the language the DB while editing
@app.route("/get_default_genre/<int:id>", methods=["GET"])
def get_default_genre(id):
    mnth = db.session.query(Collection.genre_id).filter(Collection.id == id).first()
    default_genre = mnth[0]
    return default_genre


# to select the format from the DB while editing
@app.route("/get_default_group/<int:id>", methods=["GET"])
def get_default_group(id):
    contrib = db.session.query(Timeline.group).filter(Timeline.id == id).first()
    default_group = contrib[0]
    return default_group


# null out blank year and month in DB
@app.route("/nulldb")
def nulldb():
    stmt = (
        update(Collection)
        .where(Collection.release_month == "")
        .values(release_month=None)
    )
    stmt1 = (
        update(Collection)
        .where(Collection.release_year == "")
        .values(release_year=None)
    )
    # print (stmt)
    db.session.execute(stmt)
    db.session.execute(stmt1)
    db.session.commit()
    return redirect("dashboard")


# to select the month the DB while editing


@app.route("/get_default_library/<id>", methods=["GET"])
def get_default_library(id):
    mnth = (
        db.session.query(Libcollection.library_id)
        .filter(Libcollection.id == id)
        .first()
    )
    default_library = mnth[0]
    return default_library


# to select the month the DB while editing


@app.route("/get_default_language/<int:id>", methods=["GET"])
def get_default_languagey(id):
    mnth = (
        db.session.query(Libcollection.language_id)
        .filter(Libcollection.id == id)
        .first()
    )
    default_language = mnth[0]
    return default_language


# to select the month the DB while editing


@app.route("/get_default_month/<int:id>", methods=["GET"])
def get_default_month(id):
    mnth = (
        db.session.query(Collection.release_month).filter(Collection.id == id).first()
    )
    default_month = mnth[0]
    return default_month


# to select the year from the DB while editing


@app.route("/get_default_year/<int:id>", methods=["GET"])
def get_default_year(id):
    yr = db.session.query(Collection.release_year).filter(Collection.id == id).first()
    default_year = yr[0]
    return default_year


# to select the year from the DB while editing
@app.route("/get_default_date/<int:id>", methods=["GET"])
def get_default_date(id):
    day = db.session.query(Collection.release_date).filter(Collection.id == id).first()
    default_date = day[0]
    return default_date


# to select the month the DB while editing


@app.route("/get_default_monthtl/<int:id>", methods=["GET"])
def get_default_monthtl(id):
    mnth = db.session.query(Timeline.release_month).filter(Timeline.id == id).first()
    default_month = mnth[0]
    return default_month


# to select the year from the DB while editing
@app.route("/get_default_yeartl/<int:id>", methods=["GET"])
def get_default_yeartl(id):
    yr = db.session.query(Timeline.release_year).filter(Timeline.id == id).first()
    default_year = yr[0]
    return default_year


# to select the year from the DB while editing
@app.route("/get_default_datetl/<int:id>", methods=["GET"])
def get_default_datetl(id):
    day = db.session.query(Timeline.release_date).filter(Timeline.id == id).first()
    default_date = day[0]
    return default_date


# get initials from user fullname
def get_initials(fullname):
    names = fullname.split(" ")
    initials = ""
    for name in names:
        initials += name[0]
    return initials


# convert filesize to human readeadble


def convert_bytes(size):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return size


# main db backup creation funtion


def create_db_backup():
    # create a backup file name with the current date and time
    db_file = os.path.abspath(os.getcwd() + "/nml/db/nml.db")
    backup_filename = "db_file-{}.db".format(time.strftime("%Y%m%d-%H%M%S"))
    backup_location = os.path.abspath(
        os.getcwd() + "/nml/static/dbbackup/" + backup_filename
    )
    # create a copy of the database file
    os.system("cp {} {}".format(db_file, backup_location))
    # siz = convert_bytes(os.path.getsize(backup_location))
    tar = tarfile.open(backup_location + ".tar.gz", "w:gz")
    for name in [backup_location]:
        tar.add(name)
        siz = convert_bytes(os.path.getsize(backup_location + ".tar.gz"))
    tar.close()
    if os.path.isfile(backup_location):
        os.remove(backup_location)
    # os.remove(backup_filename)

    return [backup_filename + ".tar.gz", siz]



# create tar file backup
@app.route("/tarbackup", methods=["GET"])
def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


# use ntfy to send notifications to ntfy app
def ntfysend(message):
    try:
        print ("not empty")
        if not " " in server or subscription:
            print ("sending_text")
            requests.post("https://"+server+"/"+subscription,data= message.encode(encoding='utf-8'))
    except:
        print ("caught")
        return "error"
    
# check if the current logged in user is admin or not
def checkifadmin(user_id):
    if current_user.is_admin == True:
        return "go"
    else:
        flash("Access Denied. Re-directing to Dashboard", category="danger")
        return redirect(url_for("dashboard"))


# generate the file lists for db backup page


def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try:
        lst = os.listdir(path)
    except OSError:
        pass  # ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree["children"].append(make_tree(fn))
            else:
                # file_size = f'{os.path.getsize(fn)/float(1<<20):.0f} MB'
                file_size = convert_bytes(os.path.getsize(fn))
                date_string = name[8:16]
                dbdate = datetime.strptime(date_string, "%Y%m%d").date()

                tree["children"].append(
                    dict(name=name, size=file_size, backup_date=dbdate)
                )
    return tree


#function to create a temporary audio clip from the full length
def play_audio(fname):
    audio_file_path = os.path.join(os.getcwd(), "nml", "static", "music", fname)
    if os.path.exists(audio_file_path):
        size= os.path.getsize(audio_file_path)
        
        if size >0:
            audio = AudioSegment.from_file(audio_file_path, format="mp3")
        # Load and process the audio
            audio_segment = audio[:audio_length]  # 15 seconds * 1000 milliseconds/second
            # Save the extracted segment to a temporary file
            hash = hashlib.md5(fname.encode("UTF-8")).hexdigest()
            temp_file_path = os.path.join(
                os.getcwd(), "nml", "static", "music", hash + ".mp3"
            )  #'/nml/static/music/hash'
            audio_segment.export(temp_file_path, format="mp3")
            temp_audio = "/static/music/" + hash + ".mp3"
        # return send_file(temp_file_path, as_attachment=False)
        else:
            temp_audio = "/static/temp.mp3"
        return temp_audio    
        
    
# function to delete old backups, the ndays is specified in the environment variables
def purge_backups(ndays):
    path = os.path.abspath(os.getcwd() + "/nml/static/dbbackup/")
    # path = r"c:\users\%myusername%\downloads"
    now = time.time()
    deleted_count = 0
    if os.listdir(path):
        for f in os.listdir(path):
            fileloc = path + "/" + f
            size = convert_bytes(os.path.getsize(fileloc))
            if os.stat(fileloc).st_mtime < now - ndays * 86400:
                # print (f)
                if os.path.isfile(fileloc):
                    os.remove(fileloc)
                    deleted_count += 1
        if deleted_count > 0:
            flash(
                f"Successfully deleted {deleted_count} backups older than {ndays} days",
                category="success",
            )

            return deleted_count
        else:
            flash(f"No files to delete older than {ndays} days", category="info")

            return deleted_count
    else:
        flash(f"Nothing to delete", category="info")
    return deleted_count

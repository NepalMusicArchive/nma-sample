from flask import render_template, url_for, redirect, flash, request, jsonify

# from nml import app, db, bcrypt, mail
from nml import *
import json

# from nml.config.config import *
from nml.forms import *
from nml.models import (
    User,
    Collectors,
    get_count,
    get_all,
    Media,
    Format,
    Collection,
    Company,
    Timeline,
)
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.sql import func, desc, asc, or_, and_
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from datetime import datetime, timezone
from flask_mail import Mail, Message
import time
import os
import calendar
from nml.functions import *
import random
from werkzeug.utils import secure_filename

now = datetime.now()

left_edge, right_edge, left_current, right_current = search_options


@app.route('/multiple', methods=['GET', 'POST'])
def upload_files():
    form = UploadForm()
    if form.validate_on_submit():
        files = form.files.data
        for file in files:
            # Save each uploaded file to a folder
            file.save('uploads/' + file.filename)
        return 'Files uploaded successfully!'
    return render_template('input_form.html', form=form)

# status page disabled for now
@app.route("/status")
@login_required
def status():
    return render_template("status.html", title="Status")


# update the filenames to generate tagname nma-collectorid-format-collectionmainid
@app.route("/update-filename")
def gets_all():
    # res = get_all(Collection)
    res = db.session.query(Collection).all()
    for test in res:
        tag_format = (test.formats.name).replace(" ", "").lower()
        tagname = f"nma-{test.collector.collectionid}-{tag_format}-{test.id}"
        admin = Collection.query.filter_by(id=test.id).first()
        admin.tagname = tagname

        db.session.commit()
        # print(tagname)
    ntfysend(f"All filenames updated")
    return render_template("all.html", res=res)


@app.context_processor
def layout():
    nowactive_users = get_nowactive_users()
    form = SearchFormnew()
    bg_classes = [
        "text-bg-primary bg-opacity-25",
        "text-bg-success bg-opacity-25",
        "text-bg-warning  bg-opacity-25",
        "text-bg-info bg-opacity-25",
        "text-bg-secondary bg-opacity-25",
        "text-bg-light",
        "text-bg-dark bg-opacity-25",
    ]
    bg_class = random.choice(bg_classes)
    return dict(form=form, nowactive_users=nowactive_users, bg_class=bg_class)


# send email function
@app.route("/send-plain-mail")
def send_plain_mail(recipient, count):
    subject = f"{count} Database Backup[s] deleted"
    msg = Message(
        sender=["AMS DB Backup", "nirat@protonmail.com"],
        subject=subject,
        recipients=[recipient],
    )
    msg.html = f"<b> Database[s] deleted: {count}</b>"
    mail.send(msg)
    return "sent"


# send email function
@app.route("/send-mail")
def send_mail(recipient, file_name, file_size, backupmethod):
    subject = backupmethod + " Database Backup for " + time.strftime("%Y-%m-%d")
    try:
        if not " " in smtp_username or smtp_password: 
            print ("email sent")
            msg = Message(
                sender=["AMS DB Backup", "db@nepalmusicarchive.org"],
                subject=subject,
                recipients=[recipient],
            )

            msg.html = f'<b>{backupmethod} Database backed up Successfully: {time.strftime("%Y-%m-%d")} [ {file_size} ]</b>'
            backup_location = os.path.abspath(os.getcwd() + "/nml/static/dbbackup/" + file_name)
            filename = backup_location  # In same directory as script

            with app.open_resource(backup_location) as attachment:
                msg.attach(file_name, "application/octet-stream", attachment.read())
            mail.send(msg)
            return "sent"
        else:
            print ("errored")
            pass
    except:
        print ("catch error")
        return "errored out"

# Manual db_backup endpoint, called by backup button


@app.route("/db_backup", methods=["POST", "GET"])
@login_required
def db_backup():
    if request.method == "POST":
        file_location = create_db_backup()
        get_users = User.query.filter(
            User.db_notify == "1", User.activestate == "0"
        ).all()
        file_name, file_size = file_location
        if file_size:
            flash(
                f"DB Backed up Successfully: [{file_name} {file_size}]",
                category="success",
            )
            ntfysend(f"DB Backup Completed {file_name} - {file_size} - Automatic")
        else:
            flash(f"DB Backed up failed:", category="danger")
            ntfysend(f"DB Backup Failed {file_name} - {file_size} - Automatic")
        for user in get_users:
            # email_db(user.email, file_name, file_name,"Automatic")
            send_mail(user.email, file_name, file_size, "Manual")
        
        return redirect("db-download")
    else:
        return redirect("db-download")


# automated db_backup endpoint, called by cronjob


@app.route("/create-backup", methods=["GET", "POST"])
def create_backup():
    file_location = create_db_backup()
    get_users = User.query.filter(User.db_notify == "1", User.activestate == "0").all()
    file_name, file_size = file_location
    for user in get_users:
        send_mail(user.email, file_name, file_size, "Automatic")
    ntfysend(f"DB Backup Completed {file_name} - {file_size} - Automatic")
    return file_location


# generates JSON used by timeline page


# , Collection.release_year!= "", Collection.release_year!= "0"
@app.route("/create-timeline")
def create_timeline():
    get_timeline_items = (
        Collection.query.join(Format)
        .filter(
            and_(
                or_(
                    and_(Collection.release_year != "" or Collection.release_year != 0),
                    and_(
                        Collection.release_month != "" or Collection.release_month != 0
                    ),
                ),
                or_(
                    Format.id == "1",
                    Format.id == "10",
                    Format.id == "14",
                    Format.id == "3",
                ),
                Collection.format_id == Format.id,
            )
        )
        .all()
    )
    get_other_timeline_items = Timeline.query.all()

    events = []
    title = []

    # main_title = {

    #         "title": {
    #             "url": f"/static/images/nma-logo_dim.png",
    #             "caption": f"Nepal Music Archive",
    #             "credit": f"Nepal Music Archive/<a href='https://www.nepalmusicarchive.org/home'>Nepal Music Archive"
    #         },
    #         "text": {
    #             "headline": "Nepal Music Archive",
    #             "text": f"<p><p>Nepal’s first digital archive that documents music-related research papers and catalogues; and digitises analog musical content. NMA builds a musical consortium of music-related resources by connecting to various libraries (personal and public), universities, archives and institutions; make the portal accessible to not only Nepali students, musicians and music enthusiasts, but also to a global audience.</p></p>"
    #         },
    #         "group": f"Nepali Albums"
    #             }
    # title.append(main_title)
    ### hack to bring nepali album to top
    # event = {
    # "media": {
    #     "url": f"/static/images/nma-logo.png",
    #     "caption": f"Nepal Music Archive",
    #     "credit": f"Nepal Music Archive/<a href='https://www.nepalmusicarchive.org/home'>Nepal Music Archive"
    # },

    # "start_date": {
    #     "month": "",
    #     "year": "0"
    # },
    # "text": {
    #     "headline": "Nepal Music Archive",
    #     "text": f"<p><p>Nepal’s first digital archive that documents music-related research papers and catalogues; and digitises analog musical content. NMA builds a musical consortium of music-related resources by connecting to various libraries (personal and public), universities, archives and institutions; make the portal accessible to not only Nepali students, musicians and music enthusiasts, but also to a global audience.</p></p>"
    # },
    # "group": f"Nepali Albums"
    #     }
    # events.append(event)
    if get_timeline_items:
        for item in get_timeline_items:
            if item.company_id:
                company_name = item.company.name
                # print(company_name)
            else:
                company_name = ""

            if item.release_year != "" or item.release_month != "":
                if item.inscriptions:
                    # truncate inscriptions to 320 characters on timeline
                    split = item.inscriptions[:320] + " ..."
                else:
                    split = ""

                if item.collection_title == None:
                    timeline_title = "No Title"
                else:
                    timeline_title = item.collection_title

                if item.artist_id:
                    artist = item.artist_id
                else:
                    artist = ""

                if item.release_date:
                    release_date = item.release_date
                else:
                    release_date = ""

                if item.release_year:
                    release_year = item.release_year
                else:
                    release_year = ""

                if item.release_month:
                    release_month = item.release_month
                else:
                    release_month = ""

                timeline_title = timeline_title.upper()
                event = {
                    "media": {
                        "caption": f"{item.collector.collector} Collection/Nepal Music Archive",
                        "credit": f"{company_name}",
                    },
                    "start_date": {
                        "day": release_date,
                        "month": release_month,
                        "year": release_year,
                    },
                    "text": {
                        "headline": f"<a href='{url_for('collection_detail',id=item.id,pg=1)}' class='link-dark'>{timeline_title.upper()}</a>",
                        "text": f"<p>{artist}</p>",
                    },
                    "group": f"Nepali Albums",
                }
                if item.image:
                    event["media"]["url"] = f"/static/uploads/{item.image}"
                else:
                    event["media"]["url"] = "/static/images/nma-logo_dim.png"
                events.append(event)
    else:
        event = {
            "media": {
                "url": f"/static/images/nma-logo.png",
                "caption": f"Nepal Music Archive",
                "credit": f"Nepal Music Archive/<a href='https://www.nepalmusicarchive.org/home'>Nepal Music Archive",
            },
            "start_date": {"month": "11", "year": "2021"},
            "text": {
                "headline": "Nepal Music Archive",
                "text": f"<p><p>Nepal’s first digital archive that documents music-related research papers and catalogues; and digitises analog musical content. NMA builds a musical consortium of music-related resources by connecting to various libraries (personal and public), universities, archives and institutions; make the portal accessible to not only Nepali students, musicians and music enthusiasts, but also to a global audience.</p></p>",
            },
            "group": f"Nepali Albums",
        }
        events.append(event)
    if get_other_timeline_items:
        for event in get_other_timeline_items:
            title = timeline_if(event.title, "title")
            description = timeline_if(event.description, "description")
            release_date = timeline_if(event.release_date, "release_date")
            release_month = timeline_if(event.release_month, "release_month")
            release_year = timeline_if(event.release_year, "release_year")
            image = timeline_if(event.image, "image")
            credit = timeline_if(event.credit, "credit")
            group = timeline_if(event.group, "group")
            # print (release_date,release_month,release_year,group)
            timeline_title = title.upper()

            event = {
                "media": {
                    # "caption": f"Nepal Music Archive",
                    "credit": f"{credit}"
                },
                "start_date": {
                    "day": release_date,
                    "month": release_month,
                    "year": release_year,
                },
                "text": {
                    "headline": f"{timeline_title.upper()}",
                    "text": f"<p>{description}</p>",
                },
                "group": f"{group}",
            }
            if image:
                # print(image)
                event["media"]["url"] = f"/static/uploads/timeline/{image}"
                # event["media"]["url"] = '/static/images/nma-logo.png'
            else:
                event["media"]["url"] = "/static/images/nma-logo.png"
            events.append(event)

    # main_title = {
    #     "media": {
    #         "url": "/static/images/nma-logo.png",
    #         "caption": "Nepal Music Archive",
    #         "credit": "Nepal Music Archive/<a href='https://www.nepalmusicarchive.org/home'>Nepal Music Archive</a>"
    #     },

    #     "start_date": {
    #         "month": "",
    #         "year": "1800"
    #     },
    #     "text": {
    #         "headline": "Nepal Music Archive<br/>",
    #         "text": "<p>Nepal’s first digital archive that documents music-related research papers and catalogues; and digitises analog musical content. NMA builds a musical consortium of music-related resources by connecting to various libraries (personal and public), universities, archives and institutions; make the portal accessible to not only Nepali students, musicians and music enthusiasts, but also to a global audience.</p>"
    #     },
    #     "group": f"Nepali Albums"
    # }
    # create the main timeline data in JSON format
    timeline_data = {
        # "title": main_title,
        "events": events
    }
    # return timeline_data
    with open("nml/static/timeline/timeline.json", "w") as json_file:
        json_data = json.dump(timeline_data, json_file)

    # return timeline_data
    
    ntfysend("Timeline created")
    
    return render_template("timeline/timeline.html")


@app.route("/timeline_list/<int:page_num>", methods=["POST", "GET"])
@login_required
def timeline_list(page_num):
    show_details = Timeline.query.order_by(Timeline.release_year.desc()).paginate(
        per_page=items_per_page, page=page_num, error_out=True
    )

    return render_template(
        "timeline/list_timeline.html",
        title="Timeline List",
        show_details=show_details,
        search_options=search_options,
    )

@app.route("/show_timeline_list", methods=["POST", "GET"])
@login_required
def show_timeline_list():
    show_details = Timeline.query.order_by(Timeline.release_year.desc()
    )

    return render_template(
        "timeline/list-timeline.html",
        title="Timeline List",
        show_details=show_details,
        search_options=search_options,
    )


@app.route("/edit_event/<int:id>/<int:pg>", methods=["GET", "POST"])
@login_required
def edit_event(id, pg):
    form = AddTimeline()
    show_details = Timeline.query.filter_by(id=id).first()
    get_all_timeline = db.session.query(Timeline.group.distinct().label("group"))
    titles = [row.group for row in get_all_timeline.all()]
    default_group = get_default_group(id)
    default_monthtl = get_default_monthtl(id)
    default_datetl = get_default_datetl(id)
    default_yeartl = get_default_yeartl(id)
    form.release_month.default = default_monthtl
    form.release_date.default = default_datetl
    form.release_year.default = default_yeartl
    form.group.default = default_group

    if get_all_timeline:
        form.group.choices = [
            (group.group, group.group) for group in get_all_timeline.all()
        ]
        form.group.choices = [("0", "Choose Grouping")] + form.group.choices
    else:
        form.group.choices = [("0", "No Grouping")]

    form.release_month.choices = [("", "Month")] + [
        (x, calendar.month_name[x]) for x in range(1, 13)
    ]

    form.release_date.choices = [("", "Date")] + [(x, x) for x in range(1, 32)]

    form.release_year.choices = [("", "Year")] + [
        (x, x) for x in range(1800, now.year + 1)
    ]

    if request.method == "POST":
        timeline_info = Timeline.query.get(id)
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/timeline/")
        # print (form.title.data)

        if form.release_month.data == "":
            release_month = None
        else:
            release_month = form.release_month.data

        # if form.title.data =="":
        #     title = None
        # else:
        if form.title.data == "":
            title = None
        else:
            title = form.title.data
        # print(f'from form: {form.collection_title.data}, from var:{title}')

        if form.credit.data == "":
            credit = None
        else:
            credit = form.credit.data

        if form.release_year.data == "":
            release_year = None
        else:
            release_year = form.release_year.data

        if form.release_date.data == "":
            release_date = None
        else:
            release_date = form.release_date.data

        if form.description.data == "":
            description = None
        else:
            description = form.description.data

        if request.files["image"]:
            file = request.files["image"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)
            file.save(f"{upload_path}/{timeline_info.id}_timeline{file_extension}")
            image = f"{timeline_info.id}_timeline{file_extension}"
            timeline_info.image = image

        timeline_info.group = form.group.data
        timeline_info.release_date = release_date
        timeline_info.release_month = release_month
        timeline_info.release_year = release_year
        timeline_info.credit = credit
        timeline_info.title = title
        timeline_info.description = description

        db.session.commit()
        return redirect(url_for("show_timeline_list", page_num=pg))

    form.description.data = show_details.description
    form.title.data = show_details.title
    form.credit.data = show_details.credit
    return render_template(
        "timeline/edit_event.html",
        title="Edit Timeline Event",
        form=form,
        show_details=show_details,
    )


# timeline event delete function
@app.route("/event_delete/<int:id>")
@login_required
def event_delete(id):
    timeline = Timeline.query.get_or_404(id)
    try:
        db.session.delete(timeline)
        db.session.commit()
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/timeline/")
        os.remove(f"{upload_path}/{timeline.image}")
        flash(f"Event Deleted.", category="info")
        return redirect(url_for("show_timeline_list", page_num="1"))
    except Exception as E:
        flash(f"Cannot delete Event!!!", category="danger")
        return redirect(url_for("show_timeline_list", page_num="1"))


@app.route("/add_timeline_events", methods=["POST", "GET"])
@login_required
def add_timeline_events():
    per_page = items_per_page
    form = AddTimeline()
    page_num = 1
    get_data = Timeline.query.order_by(Timeline.id.desc()).paginate(
        per_page=items_per_page, page=page_num, error_out=True
    )
    get_all_timeline = db.session.query(Timeline.group.distinct().label("group"))
    titles = [row.group for row in get_all_timeline.all()]
    get_latest = Timeline.query.order_by(Timeline.id.desc()).first()
    next_entry_id = get_latest.id + 1
    # print (titles)
    if get_all_timeline:
        form.group.choices = [
            (group.group, group.group) for group in get_all_timeline.all()
        ]
        form.group.choices = [("0", "Choose Grouping")] + form.group.choices
    else:
        form.group.choices = [("0", "No Grouping")]

    form.release_month.choices = [("", "Month")] + [
        (x, calendar.month_name[x]) for x in range(1, 13)
    ]

    form.release_date.choices = [("", "Date")] + [(x, x) for x in range(1, 32)]

    form.release_year.choices = [("", "Year")] + [
        (x, x) for x in range(1800, now.year + 1)
    ]
    if request.method == "POST":
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/timeline/")
        if form.release_month.data == "":
            release_month = None
        else:
            release_month = form.release_month.data

        if form.release_year.data == "":
            release_year = None
        else:
            release_year = form.release_year.data

        if form.release_date.data == "":
            release_date = None
        else:
            release_date = form.release_date.data

        if form.title.data == "":
            title = None
        else:
            title = form.title.data

        if form.description.data == "":
            description = None
        else:
            description = form.description.data

        if form.credit.data == "":
            credit = None
        else:
            credit = form.credit.data
        # print(form.group.data)
        if form.group.data == "" or form.group.data == "0":
            group = None
            flash(f"Timeline cannot be added . Missing Group", category="danger")
            return redirect(url_for("add_timeline_events"))
        else:
            group = form.group.data

            sub = Timeline(
                id=next_entry_id,
                title=title,
                description=description,
                release_month=release_month,
                release_date=release_date,
                release_year=release_year,
                credit=credit,
                group=group,
            )

            if request.files["image"]:
                file = request.files["image"]
                filename = file.filename
                file_name, file_extension = os.path.splitext(filename)
                sub.image = str(next_entry_id) + "_timeline" + file_extension
                file.save(f"{upload_path}/{sub.image}")

            db.session.add(sub)
            db.session.commit()
            flash(
                f'Timeline added Successfully. Title : <span class="user-select-all">{title}</span>',
                category="success",
            )

            # session.query(ObjectRes).order_by(ObjectRes.id.desc()).first()
            return redirect(url_for("add_timeline_events"))

    return render_template(
        "timeline/add_timeline.html",
        title="Add Timeline Events",
        form=form,
        next_entry_id=next_entry_id,
        search_options=search_options,
        get_data=get_data,
    )


@app.route("/show_language/", defaults={"id": 0}, methods=["POST", "GET"])
@app.route("/show_language/<int:id>", methods=["POST", "GET"])
@login_required
def show_language(id):
    form = AddLanguage()
    show_details = Language.query.all()
    if form.validate_on_submit():
        if id:
            found = Language.query.filter_by(name=form.language.data).first()
            if found:
                flash(
                    f"Language already exists: {form.language.data} ",
                    category="warning",
                )
            else:
                filter = Language.query.filter_by(id=id).first()
                filter.name = form.language.data
                db.session.commit()
                flash(f"Language Edited: {filter.name} ", category="success")

            return redirect(url_for("show_language"))
            pass

        else:
            found = Language.query.filter_by(name=form.language.data).first()
            if found:
                flash(
                    f"Language already exists: {form.language.data} ",
                    category="warning",
                )
            else:
                language_add = Language(name=form.language.data)
                db.session.add(language_add)
                db.session.commit()
                flash(
                    f"Language added successfully: {form.language.data}",
                    category="success",
                )
            return redirect(url_for("show_language", page_num=1))
            pass
    else:
        if id:
            # Load the record data from the database and populate the form
            filter = Language.query.filter_by(id=id).first()
            form.language.data = filter.name
            id = filter.id
            pass
    return render_template(
        "add_language.html",
        title="Language List",
        show_details=show_details,
        form=form,
        id=id,
        search_options=search_options,
    )


# user delete function
@app.route("/language_delete/<int:id>")
@login_required
def language_delete(id):
    user = Language.query.get_or_404(id)
    try:
        filter = Collection.query.filter_by(language_id=id).first()
        if filter:
            flash(
                f"Cannot delete Language!!! Some Collections have this Language ({user.name})",
                category="danger",
            )
            return redirect(url_for("show_language"))
        else:
            # print('no')

            db.session.delete(user)
            db.session.commit()
            flash(f"Language Deleted : {user.name} ", category="info")
            return redirect(url_for("show_language"))

    except Exception as E:
        flash(f"Cannot delete Language!!!", category="danger")
        return redirect(url_for("Language"))

from flask import render_template, url_for, redirect, flash, request, jsonify, send_file

# from nml import app, db, bcrypt, mail
from nml import *
import json

# from nml.config.config import *
from nml.forms import *
from nml.models import *
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.sql import func, desc, asc, or_, and_
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from datetime import datetime, timezone
from flask_mail import Mail, Message
import time
import os
import calendar
from nml.functions import *
from nml.insert import *
from nml.actions import *
from nml.datasets import *
from datetime import datetime
import requests
from geopy.distance import geodesic

import socket


# split environment variables for search pagination options
left_edge, right_edge, left_current, right_current = search_options

# get current date_time to use in various places e.g: addcollection, db backup etc
now = datetime.now()

# display timeline page (json file is loaded by using /create-timeline URL)


@app.route("/timeline")
@login_required
def timeline():
    return render_template("timeline/timeline.html")


# main route for the homepage
@app.route("/")
@app.route("/home")
@login_required
def homepage():
    return render_template("homepage.html", title="Home")


location_data = {}

@app.route("/check")
def check():
    # print (f'{location_data}  is this')
    if location_data:
        # print ('there is something')
        latitude = location_data["latitude"]
        longitude = location_data["longitude"]
        home = (latitude, longitude)
        library = (27.679437, 85.283187)
        # Print the distance calculated in km
        dist = int(geodesic(home, library).km)
        dist = str(dist)
        return f"{dist} km(s) away"
    return render_template("location.html", location_data=location_data)


@app.route("/location", methods=["POST", "GET"])
def location():
    data = request.json
    latitude = data["latitude"]
    longitude = data["longitude"]

    # Save the location data to the Python variable
    global location_data
    location_data["latitude"] = latitude
    location_data["longitude"] = longitude
    session["location_data"] = {"latitude": latitude, "longitude": longitude}
    # print (location_data['latitude'], location_data['longitude'])
    home = (latitude, longitude)
    # print(f"home address: {home}")
    library = (27.679437, 85.283187)
    # Print the distance calculated in km
    dist = int(geodesic(home, library).km)
    dist = str(dist)
    # print(f'walking distance {dist} km') str(j) +
    # print (f'{dist} km away')
    return "found"


# displays the DB Backup/Download page, uses functions make_tree (in functions.py)
@app.route("/db-download", methods=["GET", "POST"])
@login_required
def db_download():
    if checkifadmin(current_user.id) == "go":
        path = os.path.abspath(os.getcwd() + "/nml/static/dbbackup/")
        return render_template(
            "db_download.html",
            tree=make_tree(path),
            path="dbbakup/",
            title="Database Backups",
            db_backup=create_backup,
            purge_backup_days=purge_backup_days,
        )
    else:
        return redirect(url_for("login"))


# DB cleanup endpoint, called by cronjob, can also be called through environment variables


@app.route("/purge-backup/<int:ndays>", methods=["GET", "POST"])
def db_purge(ndays):
    # print(ndays)
    get_users = User.query.filter(User.db_notify == "1", User.activestate == "0").all()
    out = purge_backups(ndays)
    count = out
    for user in get_users:
        send_plain_mail(user.email, count)
    return redirect("/db-download")


# calls the dashboard template


@app.route("/dashboard")
@login_required
def dashboard():
    # user = get_count(User)
    collector_count = get_count(Collectors)
    # get_all_format = get_all(Format)
    get_collectors = Collectors.query.all()
    get_collection_count = get_count(Collection)
    get_publications = get_count(Libcollection)
    get_companies = get_count(Company)
    totald = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == False
                )  # Adjust the condition for enabled as needed
                or (Collection.activestate == False)
            )
            .count()
        )
    # Query the database to get a list of formats and their count
    last_entry = Collection.query.order_by(Collection.date_added.desc()).first()
    last_entryp = Libcollection.query.order_by(Libcollection.date_added.desc()).first()
    session = db.session
    media_counts = (
        session.query(Collection.media_id, func.count().label("count"))
        .group_by(Collection.media_id)
        .all()
    )
    media_count_dict = {}

    for media_id, count in media_counts:
        percentage = get_percent(get_collection_count,count)
        media_name = session.query(Media).filter_by(id=media_id).first().name
        media_count_dict[media_name] = {'count': count, 'percentage': percentage}
        
    
        
    # for media_name, count in media_count_dict.items():
    #     print(f"Media Type: {media_name}, Count: {count}")

    formats_per_collector = (
        db.session.query(
            Collectors.collector,
            Collectors.id,
            Format.name,
            Format.id,
            db.func.count(Format.id),
        )
        .join(Collection, Collectors.id == Collection.collector_id)
        .join(Format, Format.id == Collection.format_id)
        .group_by(Collectors.collector, Collectors.id, Format.name, Format.id)
        # .order_by(asc(Collectors.collector))
        .all()
    )

    formats_dict = {}
    for collector, collector_id, format, format_id, count in formats_per_collector:
        if collector not in formats_dict:
            formats_dict[collector] = {"collector_id": collector_id}
        formats_dict[collector][format] = count

    counts = {}
    for collector, formats in formats_dict.items():
        distinct_count = len(set(formats.keys()))
        # total_count = sum(formats.values())
        total_count = sum(formats[key] for key in formats if key != "collector_id")
        counts[collector] = {"total_count": total_count, "formats": formats}

    all_formats = set()
    for collector, collector_id, format_id, format, count in formats_per_collector:
        all_formats.add((format_id, format))
    all_formats = list(all_formats)

    format_totals = {}
    for collector, format_counts in formats_dict.items():
        for format, count in format_counts.items():
            if format not in format_totals:
                format_totals[format] = 0
            format_totals[format] += count


    drecord_counts = (
        db.session.query(Collectors.collector, func.count(Collection.id))
        .join(Collection).
        filter(Collection.activestate==False)
        .group_by(Collectors.collector)
        .all()
    )
    #print (drecord_counts)

    drecord_counts_dict = {}
    
    for record in drecord_counts:
        username = record[0]
        count = record[1]
        drecord_counts_dict[username] = count
    
   # print (drecord_counts_dict)
    
    unique_artist_ids = set()

    # Iterate through the collections and add unique artist IDs to the set
    for collection in Collection.query.all():
        unique_artist_ids.add(collection.artist_id)

    # Calculate the count of unique artists
    unique_artist_count = len(unique_artist_ids)

    # Get the total number of libraries
    total_libraries = session.query(func.count(Library.id)).scalar()

    # Get the count of records for each library
    library_counts = (
        session.query(Library.id, Library.name, func.count(Libcollection.id))
        .join(Libcollection)
        .group_by(Library.id, Library.name)
        .all()
    )
    # Session = sessionmaker(bind=db.engine)

    # Query to count duplicates based on ISBN and title
    duplicate_counts = (
        session.query(
            Libcollection.isbn, Libcollection.title, func.count().label("count")
        )
        .group_by(Libcollection.isbn, Libcollection.title)
        .having(func.count() > 1)
        .all()
    )

    # Print the duplicates and their counts
    # for duplicate in duplicate_counts:
    # print(f"ISBN: {duplicate.isbn}, Title: {duplicate.title}, Count: {duplicate.count}")

    double_copy = sum(d.count for d in duplicate_counts)

    # print(f"Total count of duplicates: {total_count}")

    return render_template(
        "dashboard.html",
        title="Dashboard",
        collector_count=collector_count,
        format_totals=format_totals,
        counts=counts,
        formats_dict=formats_dict,
        all_formats=all_formats,
        get_collectors=get_collectors,
        collectioncount=get_collection_count,
        last_entry=last_entry,
        media_count_dict=media_count_dict,
        get_publications=get_publications,
        get_companies=get_companies,
        total_libraries=total_libraries,
        library_counts=library_counts,
        double_copy=double_copy,
        last_entryp=last_entryp,
        unique_artist_count=unique_artist_count,
        totald=totald,
        drecord_counts=drecord_counts_dict,
    )


# displays the users page
@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    active_users = (
        db.session.query(func.count(User.id)).filter(User.activestate == False).scalar()
    )

    # Count the number of admin users
    admin_users = (
        db.session.query(func.count(User.id)).filter(User.is_admin == True).scalar()
    )

    # Count the number of emailed users
    email_users = (
        db.session.query(func.count(User.id)).filter(User.db_notify == True).scalar()
    )

    # Count the total number of users
    total_users = db.session.query(func.count(User.id)).scalar()

    if checkifadmin(current_user.id) == "go":
        # listusers = get_all(User)
        listusers = User.query.all()
        record_counts = (
            db.session.query(User.username, func.count(Collection.id))
            .join(Collection)
            .group_by(User.username)
            .all()
        )

        record_counts_dict = {}

        for record in record_counts:
            username = record[0]
            count = record[1]
            record_counts_dict[username] = count

        all_users = User.query.all()

        form = RegisterForm()
        if form.validate_on_submit():
            encrypted_password = bcrypt.generate_password_hash(
                form.password.data
            ).decode("utf-8")
            user = User(
                username=form.username.data,
                email=form.email.data,
                fullname=form.fullname.data,
                is_admin=form.is_admin.data,
                db_notify=form.email_notify.data,
                password=encrypted_password,
            )
            db.session.add(user)
            db.session.commit()
            flash(
                f"Account Created Successfully: {form.username.data}",
                category="success",
            )
            return redirect(url_for("users"))
        return render_template(
            "users.html",
            title="Users",
            form=form,
            user_list=listusers,
            all_users=all_users,
            record_counts=record_counts_dict,
            active_users=active_users,
            admin_users=admin_users,
            total_users=total_users,
            email_users=email_users,
        )
    else:
        return redirect(url_for("users"))


# callled by collection disables/enables the collection item
@app.route("/active_inactivec", methods=["POST"])
@login_required
def active_inactivec():
    status = request.form["status"]
    coll_id = request.form["id"]
    # page_num = request.form["page_num"]
    # print (f'"collection id:" {coll_id}')
    get_coll = Collection.query.filter_by(id=coll_id).first()
    # print(get_coll)
    
    if status == "public":
        get_coll.activestate = False
        # Update the record's status to public
    elif status == "private":
        get_coll.activestate = True
    db.session.commit()
    return redirect(url_for("allcollection"))


# callled by collection disables/enables the collection item
@app.route("/active_inactives", methods=["POST"])
@login_required
def active_inactives():
    status = request.form["status"]
    coll_id = request.form["id"]
    page_num = request.form["page_num"]
    search_term = request.form["search_term"]
    get_coll = Collection.query.filter_by(id=coll_id).first()
    # print(get_coll)
    if status == "public":
        get_coll.activestate = False
        # Update the record's status to public
    elif status == "private":
        get_coll.activestate = True
    db.session.commit()
    return redirect(url_for("search", search_term=search_term, page_num=page_num))


# callled by contributors disables/enables the active contributors
@app.route("/active_inactive", methods=["POST"])
@login_required
def active_inactive():
    status = request.form["status"]
    coll_id = request.form["id"]
    get_coll = Collectors.query.filter_by(id=coll_id).first()
    get_collection = Collection.query.filter_by(collector_id=coll_id).first()
    # print(get_coll)
    # print(status)
    # print (get_collection)
    if status == "public":
        get_coll.activestate = False
        
        collections_to_update = Collection.query.filter_by(collector_id=coll_id).all()
        for collection in collections_to_update:
            collection.activestate = False
        # Update the record's status to public
    elif status == "private":
        get_coll.activestate = True
        
        collections_to_update = Collection.query.filter_by(collector_id=coll_id).all()
        for collection in collections_to_update:
            collection.activestate = True

    db.session.commit()
    return redirect(url_for("contributors"))


# recording company details add / edit


# @app.route('/record_company', methods=['GET', 'POST'])
@app.route("/record_company/", defaults={"id": 0}, methods=["POST", "GET"])
@app.route("/record_company/<int:id>", methods=["POST", "GET"])
@login_required
def record_company(id):
    # id = ""
    form = AddCompany()
    companies = get_all(Company)
    # companies = Company.query.all()
    if form.validate_on_submit():
        if id:
            filter = Company.query.filter_by(id=id).first()
            filter.name = form.company.data
            db.session.commit()
            flash(f"Company Edited: {filter.name} ", category="success")
            return redirect(url_for("record_company"))
            pass
        else:
            found = Company.query.filter_by(name=form.company.data).first()
            # print (found)

            if found:
                flash(
                    f"Company already exists: {form.company.data} ", category="warning"
                )
            else:
                genre_add = Company(name=form.company.data)
                db.session.add(genre_add)
                db.session.commit()
                flash(
                    f"Company added successfully: {form.company.data}",
                    category="success",
                )
            return redirect(url_for("record_company", page_num=1))
            pass
    else:
        if id:
            # Load the record data from the database and populate the form
            filter = Company.query.filter_by(id=id).first()
            form.company.data = filter.name
            id = filter.id
            pass

        # if form.validate_on_submit():
    #     found = Company.query.filter_by(
    #         name=form.company.data).first()
    #     # print (found)
    #     if found:
    #         # print('Already Exists')
    #         flash(
    #             f'Company already exists: {form.company.data}', category='warning')
    #         return redirect(url_for('record_company'))
    #     else:
    #         company = Company(name=form.company.data)
    #         db.session.add(company)
    #         db.session.commit()
    #         flash('Record Company Added.', category='success')
    #         return redirect(url_for('record_company'))
    # else:
    #     if id:
    #         # Load the record data from the database and populate the form
    #         filter=Company.query.filter_by(id=id).first()
    #         form.company.data=filter.name
    #         id=filter.id
    #         pass

    return render_template(
        "record_company.html",
        title="Record Companies",
        companies=companies,
        form=form,
        id=id,
        search_options=search_options,
    )


# collector delete function, will not delete if any collector has data entered in any collection
@app.route("/companydelete/<int:id>")
@login_required
def companydelete(id):
    company = Company.query.get_or_404(id)
    try:
        db.session.delete(company)
        db.session.commit()
        flash(f"Record Company Deleted.", category="info")
        return redirect(url_for("record_company"))
    except Exception as E:
        flash(f"Cannot delete Record Company !!!", category="danger")
        return redirect(url_for("record_company"))


# function called to display format according to selected media


@app.route("/format/<int:medias>")
@login_required
def showformat(medias):
    format_list = Format.query.filter_by(media_id=medias).order_by(Format.name.asc())

    formatArray = []
    formatArray.append({"id": "0", "name": "Select Format"})
    for formats in format_list:
        formatsObj = {}
        formatsObj["id"] = formats.id
        formatsObj["name"] = formats.name
        formatArray.append(formatsObj)

    return jsonify({"format_list": formatArray})


# format delete function will not delete if format is used in any collection
@app.route("/formatdelete/<int:id>")
@login_required
def formatdelete(id):
    format = Format.query.get_or_404(id)
    try:
        db.session.delete(format)
        db.session.commit()
        flash(f"Format Deleted: {format.name} ", category="info")
        return redirect(url_for("formats"))
    except Exception as E:
        flash(
            f"Cannot Delete!!! Some Collections have this format !", category="danger"
        )
        return redirect(url_for("formats"))
        # return unicode(E)


# media delete function, will not delete if media is used in any collection


@app.route("/mediadelete/<int:id>")
@login_required
def mediadelete(id):
    media = Media.query.get_or_404(id)
    try:
        db.session.delete(media)
        db.session.commit()
        flash(f"Media Deleted: {media.name} ", category="info")
        return redirect(url_for("formats"))
    except Exception as E:
        # return render_template('error.html', message='A pending rollback error occurred')
        flash(f"Cannot Delete!!! Some Collections have this media !", category="danger")
        return redirect(url_for("formats"))
        # return unicode(E)


# contributors page, allows adding new contributors


@app.route("/contributors", defaults={"id": 0}, methods=["GET", "POST"])
@app.route("/contributors/<int:id>", methods=["POST", "GET"])
@login_required
def contributors(id):
    form = AddCollector()
    # collectors = get_all(Collectors)
    sort_by = request.args.get(
        "sort_by", "collectionid"
    )  # Default to sorting by collectionid
    sort_order = request.args.get("sort_order", "asc")  # Default to ascending order

    # Define a dictionary to map column names to SQLAlchemy attributes
    column_mapping = {
        "collectionid": Collectors.collectionid,
        "collector": Collectors.collector,
    }

    if sort_by not in column_mapping:
        sort_by = "collectionid"  # Default to sorting by collectionid

    # Define the sorting order
    if sort_order == "asc":
        sorting_order = column_mapping[sort_by].asc()
    else:
        sorting_order = column_mapping[sort_by].desc()

    collectors = Collectors.query.order_by(sorting_order)

    record_counts = (
        db.session.query(Collectors.collector, func.count(Collection.id))
        .join(Collection)
        .group_by(Collectors.collector)
        .all()
    )

    record_counts_dict = {}

    for record in record_counts:
        username = record[0]
        count = record[1]
        record_counts_dict[username] = count

    drecord_counts = (
        db.session.query(Collectors.collector, func.count(Collection.id))
        .join(Collection).
        filter(Collection.activestate==False)
        .group_by(Collectors.collector)
        .all()
    )
    # print (drecord_counts)

    drecord_counts_dict = {}
    
    for record in drecord_counts:
        username = record[0]
        count = record[1]
        drecord_counts_dict[username] = count
    
    # print (drecord_counts_dict)
    record_counts_dict = {}

    for record in record_counts:
        username = record[0]
        count = record[1]
        record_counts_dict[username] = count

    # Count the number of users with agreement
    agreement_users = (
        db.session.query(func.count(Collectors.id))
        .filter(Collectors.agreement == True)
        .scalar()
    )
    # Count the number of enabled contributors
    enabled_contribs = (
        db.session.query(func.count(Collectors.id))
        .filter(Collectors.activestate == True)
        .scalar()
    )
    # Count the number of disabled contributors
    disabled_contribs = (
        db.session.query(func.count(Collectors.id))
        .filter(Collectors.activestate == False)
        .scalar()
    )
    # Count the number of users without agreement
    nagreement_users = (
        db.session.query(func.count(Collectors.id))
        .filter(Collectors.agreement == False)
        .scalar()
    )
    ids = (
        Collectors.query.with_entities(Collectors.id)
        .order_by(desc(Collectors.id))
        .first()
    )
    if id:
        if int(id) < 9:
            new_id = "00" + str(id)
        else:
            new_id = "0" + str(id)

    else:
        if ids != None:
            new_id = str(int(ids[0]) + 1)
            if int(new_id) < 9:
                new_id = "00" + str(new_id)
            else:
                new_id = "0" + str(new_id)
        else:
            new_id = id
    filter = ""
    if form.validate_on_submit():
        if id:
            filter = Collectors.query.filter_by(id=id).first()
            filter.collector = form.collector.data
            filter.email = form.email.data
            filter.phone = form.phone.data
            filter.address = form.address.data
            filter.mobile = form.mobile.data
            filter.relation = form.relation.data
            filter.seccontact = form.seccontact.data
            filter.secphone = form.secphone.data
            filter.reference = form.reference.data
            filter.remarks = form.remarks.data
            filter.agreement = form.agreement.data

            db.session.commit()
            flash(f"Contributor Edited: {filter.collector} ", category="success")
            return redirect(url_for("contributors"))
            pass
        else:
            found = Collectors.query.filter_by(collector=form.collector.data).first()
            if found:
                flash(
                    f"Contributor already exists: {form.collector.data}",
                    category="warning",
                )
                return redirect(url_for("contributors"))
            else:
                # print (id)
                collector = Collectors(
                    collector=form.collector.data,
                    collectionid=form.collectionid.data,
                    address=form.address.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    mobile=form.mobile.data,
                    seccontact=form.seccontact.data,
                    relation=form.relation.data,
                    secphone=form.secphone.data,
                    reference=form.reference.data,
                    agreement=form.agreement.data,
                    remarks=form.remarks.data,
                    activestate=True,
                )
            db.session.add(collector)
            db.session.commit()
            flash("Contributor Added.", category="success")
            return redirect(url_for("contributors"))
            pass
    else:
        if id:
            # Load the record data from the database and populate the form

            filter = Collectors.query.filter_by(id=id).first()
            form.collectionid.data = filter.collectionid
            form.collector.data = filter.collector
            form.email.data = filter.email
            form.phone.data = filter.phone
            form.address.data = filter.address
            form.mobile.data = filter.mobile
            form.relation.data = filter.relation
            form.seccontact.data = filter.seccontact
            form.secphone.data = filter.secphone
            form.reference.data = filter.reference
            form.remarks.data = filter.remarks
            form.agreement.data = filter.agreement
            id = filter.id
            pass

    return render_template(
        "contributors.html",
        title="Contributors",
        new_id=new_id,
        id=id,
        form=form,
        collectors=collectors,
        ids=ids,
        filter=filter,
        agreement_users=agreement_users,
        nagreement_users=nagreement_users,
        enabled_contribs=enabled_contribs,
        disabled_contribs=disabled_contribs,
        record_counts=record_counts_dict,
        drecord_counts=drecord_counts_dict,
        
    )


# collector delete function, will not delete if any collector has data entered in any collection
@app.route("/collectordelete/<int:id>")
@login_required
def collectordelete(id):
    collector = Collectors.query.get_or_404(id)
    try:
        db.session.delete(collector)
        db.session.commit()
        flash(f"Collector Deleted.", category="info")
        return redirect(url_for("contributors"))
    except Exception as E:
        flash(f"Cannot delete contributor!!!", category="danger")
        return redirect(url_for("contributors"))


# Hidden page to register new users.
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("users"))
    form = RegisterForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )

        user = User(
            username=form.username.data,
            email=form.email.data,
            fullname=form.fullname.data,
            password=encrypted_password,
            is_admin=form.is_admin.data,
            db_notify=form.email_notify.data,
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Account Created Successfully: {form.username.data}", category="success")
        return redirect(url_for("login"))
    return render_template("signup.html", title="Signup", form=form)


# display the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.activestate == False:
                if user and bcrypt.check_password_hash(
                    user.password, form.password.data
                ):
                    user.last_active = datetime.utcnow()
                    user.login_state = 1
                    db.session.commit()
                    login_user(user)
                    flash(
                        f"Account Logged in Successfully: {form.username.data}",
                        category="success",
                    )
                    id = form.username.data
                    return redirect(url_for("dashboard"))
                else:
                    flash(
                        f"Username / Password failed. Please try again. : {form.username.data}",
                        category="danger",
                    )
            else:
                flash(
                    f"{form.username.data}, Your account has been disabled. Please contact the admin to re-activate your account",
                    category="warning",
                )
        else:
            flash(
                f"Account not found : {form.username.data} <br> Please contact the admin to get your account set up.",
                category="danger",
            )
            id = form.username.data
            return redirect(url_for("login"))

    return render_template("login.html", title="Login", form=form)


# user edit page/ change password, email notify, deactivate
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    user_list = User.query.get_or_404(id)
    record_count = (
        db.session.query(func.count(Collection.id))
        .join(User)
        .filter(User.id == id)
        .scalar()
    )
    form = ChangePassword()
    if form.validate_on_submit():
        if form.password.data:
            encrypted_password = bcrypt.generate_password_hash(
                form.password.data
            ).decode("utf-8")
            # user=User(username=form.username.data,email=form.email.data,password=encrypted_password)
            user_list.password = encrypted_password
        user_list.is_admin = form.is_admin.data
        user_list.activestate = form.activestate.data
        user_list.db_notify = form.email_notify.data
        user_list.fullname = form.fullname.data
        # print(user_list.db_notify)
        db.session.commit()
        flash("User details updated for " + user_list.fullname, category="success")
        return redirect(url_for("edit", id=user_list.id))
    return render_template(
        "edit.html",
        title="Change Password",
        form=form,
        user_list=user_list,
        record_count=record_count,
    )


# user delete function
@app.route("/userdelete/<int:id>")
@login_required
def userdelete(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"User Deleted.", category="info")
        return redirect(url_for("users"))
    except Exception as E:
        flash(f"Cannot delete User!!!", category="danger")
        return redirect(url_for("users"))


@app.post("/delete/<int:user_id>")
@login_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("users"))
    except Exception as E:
        flash(f"Cannot delete User!!!", category="danger")
        return redirect(url_for("users"))


# Display formats page
@app.route("/formats", methods=["GET", "POST"])
@login_required
def formats():
    form = AddFormat()
    form1 = AddMedia()
    media = get_all(Media)
    formats = get_all(Format)

    if media:
        form.media.choices = [(medias.id, medias.name) for medias in media]
    else:
        form.media.choices = [("0", "No Media")]

    if form1.validate_on_submit():
        found = Media.query.filter_by(name=form1.newmedia.data).first()
        # print (found)
        if found:
            # print('Already Exists')
            flash(f"Media already exists: {form1.newmedia.data}", category="warning")
            return redirect(url_for("formats"))
        else:
            # print(form1.newmedia.data)
            # return '<h1>media_id: {},Media: {}, Formats: {}, newformat: {}</h1>'.format(set_format_number.media.id, set_format_number.media.name, set_format_number.name,form.newformat.data)
            media = Media(name=form1.newmedia.data)
            db.session.add(media)
            db.session.commit()
            flash(
                f"Media Added Successfully : {form1.newmedia.data}", category="success"
            )
            return redirect(url_for("formats"))

    if form.validate_on_submit():
        found = Format.query.filter_by(
            name=form.newformat.data, media_id=form.media.data
        ).first()
        # print (found)
        if found:
            # print('Already Exists')
            flash(f"Format already exists: {form.newformat.data}", category="warning")
            return redirect(url_for("formats"))
        else:
            # print(form.media.data, form.newformat.data)
            # return '<h1>media_id: {},Media: {}, Formats: {}, newformat: {}</h1>'.format(set_format_number.media.id, set_format_number.media.name, set_format_number.name,form.newformat.data)
            format = Format(name=form.newformat.data, media_id=form.media.data)
            db.session.add(format)
            db.session.commit()
            flash(
                f"Format Added Successfully : {form.newformat.data}", category="success"
            )
            return redirect(url_for("formats"))

    return render_template(
        "formats.html", title="Formats", media=media, form1=form1, form=form
    )


# listing of all collections by contributor
@app.route(
    "/list_contributor/<int:contributor_id>/<int:format_id>/<int:page_num>",
    methods=["GET", "POST"],
)
@login_required
def list_contributor(contributor_id, format_id, page_num):
    q = contributor_id
    format_id = format_id
    per_page = items_per_page
    if format_id == 0:
        get_data = (
            Collection.query.filter(Collection.collector_id == q)
            .order_by(Collection.id.desc())
            .paginate(page=page_num, per_page=per_page, error_out=True)
        )
        get_totals = Collection.query.filter(Collection.collector_id == q).count()
        get_formatname = Collection.query.filter(Collection.collector_id == q).all()
        totald = (
            Collection.query.filter(Collection.collector_id == q).join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == False
                )  # Adjust the condition for enabled as needed
                or (Collection.activestate == False)
            )
            .count()
        )
    else:
        # get_data=Collection.query.paginate(per_page=10 ,page=page_num, error_out=True).filter(Collection.keywords.like('%'+ q +'%'))
        get_data = (
            Collection.query.filter(
                Collection.collector_id == q, Collection.format_id == format_id
            )
            .order_by(Collection.id.desc(), Collection.format_id.desc())
            .paginate(page=page_num, per_page=per_page, error_out=True)
        )
        get_totals = Collection.query.filter(
            Collection.collector_id == q, Collection.format_id == format_id
        ).count()
        totald = (
        Collection.query.filter(Collection.collector_id == q, Collection.format_id == format_id).join(
            Collectors
        )  # Assuming there's a relationship between Collection and Collector
        .filter(
            (
                Collectors.activestate == False
            )  # Adjust the condition for enabled as needed
            or (Collection.activestate == False)
        )
        .count()
        )
        get_formatname = Collection.query.filter(
            Collection.collector_id == q, Collection.format_id == format_id
        ).first()
        totald = (
            Collection.query.filter(Collection.collector_id == q, Collection.format_id == format_id).join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == False
                )  # Adjust the condition for enabled as needed
                or (Collection.activestate == False)
            )
            .count()
        )

    # get_formatname = Collection.query.filter(
    #     Collection.collector_id == q).all()
    search_string = Collectors.query.filter(Collectors.id == q).first()

    # if search_string != None:
    # print(search_options)

    return render_template(
        f"list_contributor.html",
        search_options=search_options,
        format_id=format_id,
        get_data=get_data,
        search_string=search_string,
        page=page_num,
        get_formatname=get_formatname,
        contributor_id=q,
        get_totals=get_totals,
        title="Search Results",
        totald=totald,
    )


# listing of all collections by format type
@app.route("/list_collection/<keys>/<int:page_num>", methods=["GET", "POST"])
@login_required
def list_collection(keys, page_num):
    q = keys
    per_page = items_per_page
    # get_data=Collection.query.paginate(per_page=10 ,page=page_num, error_out=True).filter(Collection.keywords.like('%'+ q +'%'))
    get_data = (
        Collection.query.filter(Collection.format_id == q)
        .order_by(Collection.id.desc())
        .paginate(page=page_num, per_page=per_page, error_out=True)
    )
    get_formatname = Collection.query.filter(Collection.format_id == q).all()
    get_totals = Collection.query.filter(Collection.format_id == q).count()
    search_string = get_formatname[0].formats.name
    #
    return render_template(
        f"list_collection.html",
        search_options=search_options,
        get_data=get_data,
        page=page_num,
        get_formatname=get_formatname,
        q=q,
        get_totals=get_totals,
        title="Search Results",
    )




# enable the search bar to work on the layouts page


# search page
@app.route("/search", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchFormnew()
    search_term = ""
    search_results = []
    search_total = ""
    if request.method == "POST":
        if form.search.data:
            search_term = form.search.data
        else:
            search_term = ""
        page = request.form.get("page_num", 1, type=int)
        per_page = request.form.get("per_page", items_per_page, type=int)
        search_results = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (
                    Collection.keywords.like("%{}%".format(search_term))
                    | Collection.inscriptions.like("%{}%".format(search_term))
                    | Collection.tagname.like("%{}%".format(search_term))
                    | Collection.collection_title.like("%{}%".format(search_term))
                    | Collection.notes.like("%{}%".format(search_term))
                )
            )
            .order_by(Collection.id.desc())
            .paginate(page=page, per_page=items_per_page, error_out=False)
        )

        # search_results = (
        #     Collection.query.filter(
        #         Collection.keywords.like("%{ }%".format(search_term))
        #         | Collection.inscriptions.like("%{ }".format(search_term))
        #         | Collection.tagname.like("%{ }".format(search_term))
        #         | Collection.collection_title.like("%{ }".format(search_term))
        #         | Collection.notes.like("%{}%".format(search_term))
        #     )
        #     .order_by(Collection.id.desc())
        #     .paginate(page=page, per_page=items_per_page, error_out=False)
        # )
        search_total = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (
                    Collection.keywords.like("%{}%".format(search_term))
                    | Collection.inscriptions.like("%{}%".format(search_term))
                    | Collection.tagname.like("%{}%".format(search_term))
                    | Collection.collection_title.like("%{}%".format(search_term))
                    | Collection.notes.like("%{}%".format(search_term))
                )
            )
            .count()
        )

    elif request.method == "GET":
        if request.args.get("search_term"):
            search_term = request.args.get("search_term")
        else:
            search_term = ""

        page = request.args.get("page_num", 1, type=int)
        per_page = request.args.get("per_page", items_per_page, type=int)
        search_results = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (Collection.activestate == True)
                & (
                    Collection.keywords.like("%{}%".format(search_term))
                    | Collection.inscriptions.like("%{}%".format(search_term))
                    | Collection.tagname.like("%{}%".format(search_term))
                    | Collection.collection_title.like("%{}%".format(search_term))
                    | Collection.notes.like("%{}%".format(search_term))
                )
            )
            .order_by(Collection.id.desc())
            .paginate(page=page, per_page=items_per_page, error_out=False)
        )
        search_total = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (Collection.activestate == True)
                & (
                    Collection.keywords.like("%{}%".format(search_term))
                    | Collection.inscriptions.like("%{}%".format(search_term))
                    | Collection.tagname.like("%{}%".format(search_term))
                    | Collection.collection_title.like("%{}%".format(search_term))
                    | Collection.notes.like("%{}%".format(search_term))
                )
            )
            .count()
        )

    return render_template(
        "search.html",
        search_options=search_options,
        form=form,
        search_results=search_results,
        search_term=search_term,
        title="Search Results",
        search_total=search_total,
    )


# run this at first run of the app, creates a blank DB with default users if db file is missing
@app.before_first_request
def create_tables():
    if not os.path.exists(("/" + str(db.engine.url).strip("sqlite:////"))):
        with app.app_context():
            db.create_all()

            adm = User(
                username="admin",
                fullname="Admin",
                email="nepalmusicarchive@gmail.com",
                password="$2b$12$Z4ZQ7vOBp.imhTBxlmHbIu7VPNe9dWlcyBUG0MIGBF21d58Fze4IO",
                is_admin=True,
                db_notify=True,
                activestate=False,
            )
            adm1 = User(
                username="jiwan",
                fullname="Jiwan Thapa Magar",
                email="jiwansahrumagar@gmail.com",
                password="$2b$12$7Qq76ofeEDfJw8k/sL9WCOsQbtyegyQ9I.4c/bxsNVlVnbowxZmvC",
                is_admin=False,
                db_notify=False,
                activestate=False,
            )
            adm2 = User(
                username="rojina",
                fullname="Rojina Tamang",
                email="rojipojii@gmail.com",
                password="$2b$12$tUAUMwG9adFW1CeXztBd..B.NIvOPoiXL943gVcyk3wqhMon50Yg6",
                is_admin=False,
                db_notify=False,
                activestate=False,
            )
            adm3 = User(
                username="appeal",
                fullname="Appeal Paudel",
                email="appeal.722@gmail.com",
                password="$2b$12$KGkbDibKL4yKj0P/H0W6huii0jzzEk8ZmIxlzvXNeCedMaoqqHyNa",
                is_admin=False,
                db_notify=False,
                activestate=False,
            )
            adm4 = User(
                username="chakshita",
                fullname="Chaksita Rana Pathak",
                email="chakshita14@gmail.com",
                password="$2b$12$8jdidxVMrm0ecLweOC.bSOMCoaaEe3vwuAv7YIInU5sS4VnhzYF4O",
                is_admin=False,
                db_notify=False,
                activestate=False,
            )
            adm5 = User(
                username="binit",
                fullname="Binit Shrestha",
                email="sbinit85@gmail.com",
                password="$2b$12$KNk.9U3NdFfnpK1ieG4qLuChTVFRZ0YZLXyTmAHmGsKr2JWrZ31F.",
                is_admin=False,
                db_notify=False,
                activestate=False,
            )
            adm6 = User(
                username="rajan",
                fullname="Rajan Shrestha",
                email="phatcowlee@gmail.com",
                password="$2b$12$.ZNIcQlOC9hAj9OBe6RGDemXZEIpZznVrTNEViyG1z9OxgQtMKIdi",
                is_admin=True,
                db_notify=True,
                activestate=False,
            )
            adm7 = User(
                username="bhushan",
                fullname="Bhushan Shilpakar",
                email="bhushan.shilpakar@gmail.com",
                password="$2b$12$qRbXE4AY0srqbl6cOAdVNeCrjuf8nTB6cDtrEFx2YG8Onao9Hjhm2",
                is_admin=True,
                db_notify=True,
                activestate=False,
            )
            adm8 = User(
                username="prabin",
                fullname="Prabin Lakhaju",
                email="plakjaju@gmail.com",
                password="$2b$12$8NLV65b.I66odAK1s9e3XOR/DIRS0eDPRd8d4CWcPnNc.nLoWjSWK",
                is_admin=False,
                db_notify=False,
                activestate=True,
            )
            adm9 = User(
                username="nirat",
                fullname="Nirat Sthapit",
                email="niratsthapit@outlook.com",
                password="$2b$12$M4N.GQtkk0cLuECHHBVj/ulRU48yQD06rj3pmU9fQxyM9MUL0v0Xa",
                is_admin=True,
                db_notify=True,
                activestate=False,
            )

            db.session.add_all(
                [adm, adm1, adm2, adm3, adm4, adm5, adm6, adm7, adm8, adm9]
            )

            db.session.commit()
    else:
        pass
        # print ('db exists')


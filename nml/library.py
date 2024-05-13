from flask import render_template, url_for, redirect, flash, request, jsonify

# from nml import app, db, bcrypt, mail
from nml import *
from nml.forms import *
import json

# from nml.config.config import *
from nml.forms import (
    LoginForm,
    RegisterForm,
    ChangePassword,
    AddCollector,
    AddMedia,
    AddFormat,
    AddCollection,
    EditCollection,
    SearchFormnew,
    AddNew,
    AddCompany,
)
from nml.models import (
    User,
    Collectors,
    get_count,
    get_all,
    Media,
    Format,
    Collection,
    Company,
    Libcollection,
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
from nml.insert import *
from nml.actions import *
import requests
from geopy.distance import geodesic

left_edge, right_edge, left_current, right_current = search_options

# import geocoder
# g = geocoder.ip('me')
# print(g.latlng)
# callled by collection disables/enables the collection item
@app.route("/active_inactivelib", methods=["POST"])
@login_required
def active_inactivelib():
    status = request.form["status"]
    coll_id = request.form["id"]
    get_coll = Library.query.filter_by(id=coll_id).first()
    # print(get_coll)
    if status == "public":
        get_coll.activestate = False
        # Update the record's status to public
    elif status == "private":
        get_coll.activestate = True
    db.session.commit()
    return redirect(url_for("add_library"))

# library items
@app.route("/publications/<int:page_num>", methods=["POST", "GET"])
@login_required
def publications(page_num):
    if current_user.is_authenticated:
        show_details = Libcollection.query.order_by(Libcollection.id.desc()).paginate(
            per_page=items_per_page, page=page_num, error_out=True
            )

        total = get_count(Libcollection)
    else:
        show_details = (
        Libcollection.query.join(
            Library
        )  # Assuming there's a relationship between Collection and Collector
        .filter(
            (
                Library.activestate == True
            )  # Adjust the condition for enabled as needed
        )
        .order_by(Libcollection.id.desc())
        .paginate(per_page=items_per_page, page=page_num, error_out=True)
        )
        
        total = (   
        Libcollection.query.join(
            Library
        )  # Assuming there's a relationship between Collection and Collector
        .filter(
            (
                Library.activestate == True
            )  # Adjust the condition for enabled as needed

        )
        .count()
        )
        

    return render_template(
        "publication/publications.html",
        title="Library Detail",
        show_details=show_details,
        get_count=total,
        page=page_num,
        search_options=search_options,
    )


dist = ""


@app.route("/publication_details/<int:id>/<int:pg>", methods=["POST", "GET"])
@login_required
def publication_details(id, pg):
    get_detail = Libcollection.query.filter_by(id=id).first()
    if get_detail.image:
        filepath = url_for("static", filename="uploads/" + get_detail.image)
    else:
        filepath = ""
        # excluding the current library
    # where_else=Libcollection.query.filter( Libcollection.title == get_detail.title , Libcollection.library_id != get_detail.library_id).all()
    # including all libraries
    where_else = Libcollection.query.filter(
        Libcollection.title == get_detail.title
    ).all()
    location_data = session.get("location_data", {})
    # print (f'loc {location_data}')
    if location_data:
        latitude = location_data["latitude"]
        longitude = location_data["longitude"]
        home = (latitude, longitude)
    else:
        home = "27.709410, 85.325274"
    distances = []
    for where in where_else:
        library = where.library.map_coordinates
        # Print the distance calculated in km
        dist = int(geodesic(home, library).km)
        dist = str(dist)
        # print (f'{dist} km away from {where.library.name}')
        distances.append(dist)
        # return f'{dist} km(s) away'
    dist = str(dist)
    return render_template(
        "publication/publication_detail.html",
        title="Publication Detail",
        get_detail=get_detail,
        where_else=where_else,
        distances=distances,
        pg=pg,
        location_data=location_data,
    )


@app.route("/add_library/", defaults={"id": 0}, methods=["POST", "GET"])
@app.route("/add_library/<int:id>", methods=["POST", "GET"])
def add_library(id):
    form = AddLibrary()
    show_details = get_all(Library)
    img = ""
    upload_path = os.path.abspath(os.getcwd() + "/nml/static/images/library/")
    if form.validate_on_submit():
        print ("reached here")
        if id:
            filter = Library.query.filter_by(id=id).first()
            print(filter)
            if form.librarian.data == "":
                librarian = None
            else:
                librarian = form.librarian.data

            if form.libraryname.data == "":
                name = None
            else:
                name = form.libraryname.data

            if form.address.data == "":
                address = None
            else:
                address = form.address.data

            if form.email.data == "":
                email = None
            else:
                email = form.email.data

            if form.contact.data == "":
                contact = None
            else:
                contact = form.contact.data

            if form.website.data == "":
                website = None
            else:
                website = form.website.data

            if form.hours.data == "":
                hours = None
            else:
                hours = form.hours.data
            
            if form.gmaps_url.data == "":
                gmurl = None
            else:
                gmurl = form.gmaps_url.data

            if form.map_coordinates.data == "":
                maps = None
            else:
                maps = form.map_coordinates.data

            filter.name = name
            filter.address = address
            filter.librarian = librarian
            filter.hours = hours
            filter.map_coordinates = maps
            filter.contact = contact
            filter.email = email
            filter.website = website
            filter.gmaps_url = gmurl
            
            if request.files["image"]:
                file = request.files["image"]
                filename = file.filename
                file_name, file_extension = os.path.splitext(filename)
                filter.image = filter.image
                file.save(f"{upload_path}/{filter.image}")

            db.session.commit()
            flash(f"Library Edited: {filter.name} ", category="success")
            return redirect(url_for("add_library"))
            pass
        else:
            # Add a new record to the database
            found = Library.query.filter_by(name=form.libraryname.data).first()
            print(found)
            # print (found)
            if found:
                print('Already Exists')
                flash(
                    f"Library already exists: {form.libraryname.data}",
                    category="warning",
                )
                return redirect(url_for("add_library"))
            else:
                sub = Library(
                    name=form.libraryname.data,
                    address=form.address.data,
                    contact=form.contact.data,
                    librarian=form.librarian.data,
                    map_coordinates=form.map_coordinates.data,
                    email=form.email.data,
                    website=form.website.data,
                    hours=form.hours.data,
                    gmurl=form.gmaps_url.data,
                )
                if request.files["image"]:
                    file = request.files["image"]
                    filename = file.filename
                    file_name, file_extension = os.path.splitext(filename)
                    sub.image = file_name + file_extension
                    file.save(f"{upload_path}/{sub.image}")
                db.session.add(sub)
                db.session.commit()
                flash("Library Added.", category="success")
                return redirect(url_for("add_library"))
                pass
    else:
        if id:
            # Load the record data from the database and populate the form
            filter = Library.query.filter_by(id=id).first()
            form.libraryname.data = filter.name
            form.address.data = filter.address
            form.contact.data = filter.contact
            form.email.data = filter.email
            form.website.data = filter.website
            form.hours.data = filter.hours
            form.map_coordinates.data = filter.map_coordinates
            form.librarian.data = filter.librarian
            form.gmaps_url.data = filter.gmaps_url
            img = filter.image
            pass
    return render_template(
        "publication/add_library.html",
        title="Libraries",
        show_details=show_details,
        form=form,
        id=id,
        img=img,
    )


@app.route(
    "/list_library/<int:library_id>/<int:page_num>",
    methods=["GET", "POST"],
)
@login_required
def list_library(library_id,page_num):
    q = library_id
    per_page = items_per_page
   
    get_data = (
        Libcollection.query.filter(Libcollection.library_id == q)
        .order_by(Libcollection.id.desc())
        .paginate(page=page_num, per_page=per_page, error_out=True)
    )
    get_totals = Libcollection.query.filter(Libcollection.library_id == q).count()
   # get_formatname = Collection.query.filter(Collection.collector_id == q).all()


    # get_formatname = Collection.query.filter(
    #     Collection.collector_id == q).all()
    search_string = Libcollection.query.filter(Libcollection.library_id == q).first()
    print (search_string)

    # if search_string != None:
    # print(search_options)

    return render_template(
        f"publication/list_library.html",
        search_options=search_options,
        show_details=get_data,
        search_string=search_string,
        page=page_num,
        contributor_id=q,
        get_totals=get_totals,
        title="Search Results",
    )


@app.route("/edit_publication/<int:id>/<int:pg>", methods=["GET", "POST"])
@login_required
def edit_publication(id, pg):
    form = AddPublication()
    get_detail = Libcollection.query.filter_by(id=id).first()
    default_library = get_default_library(id)
    default_language = get_default_languagey(id)

    # print("library dfa" + default_library)
    form.library.default = default_library
    form.language.default = default_language

    if get_detail.image:
        filepath = url_for("static", filename="uploads/" + get_detail.image)
    else:
        filepath = ""
    get_all_language = get_all(Language)
    get_all_libraries = get_all(Library)

    if get_all_language:
        form.language.choices = [(langs.id, langs.name) for langs in get_all_language]
        form.language.choices = [("0", "Choose Language")] + form.language.choices
    else:
        form.language.choices = [("0", "No Language")]

    if get_all_libraries:
        form.library.choices = [
            (library.id, library.name) for library in get_all_libraries
        ]
        form.library.choices = [("0", "Choose Library")] + form.library.choices
    else:
        form.library.choices = [("0", "No Library")]

    if request.method == "POST":
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/publication/")
        publication_info = Libcollection.query.get(id)
        if form.title.data == "":
            title = None
        else:
            title = form.title.data

        if form.library.data == "":
            library = None
        else:
            library = form.library.data

        if form.language.data == "":
            language = None
        else:
            language = form.language.data

        if form.author.data == "":
            author = None
        else:
            author = form.author.data

        if form.editor.data == "":
            editor = None
        else:
            editor = form.editor.data

        if form.publisher.data == "":
            publisher = None
        else:
            publisher = form.publisher.data

        if form.year.data == "":
            year = None
        else:
            year = form.year.data

        if form.isbn.data == "":
            isbn = None
        else:
            isbn = form.isbn.data

        if form.category.data == "":
            category = None
        else:
            category = form.category.data

        if form.edition.data == "":
            edition = None
        else:
            edition = form.edition.data

        if form.remarks.data == "":
            remarks = None
        else:
            remarks = form.remarks.data
        if request.files["image"]:
            file = request.files["image"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)
            file.save(
                f"{upload_path}/{publication_info.id}_{publication_info.library_id}{file_extension}"
            )
            image = (
                f"{publication_info.id}_{publication_info.library_id}{file_extension}"
            )
            publication_info.image = image

        publication_info.title = title
        publication_info.author = author
        publication_info.editor = editor
        publication_info.publisher = publisher
        publication_info.year = year
        publication_info.isbn = isbn
        publication_info.category = category
        publication_info.edition = edition
        publication_info.remarks = remarks
        publication_info.library_id = library
        publication_info.language_id = language

        db.session.commit()
        return redirect(url_for("publications", page_num=pg))

        # print(publication_info)

    form.title.data = get_detail.title
    form.author.data = get_detail.author
    form.editor.data = get_detail.editor
    form.publisher.data = get_detail.publisher
    form.year.data = get_detail.year
    form.isbn.data = get_detail.isbn
    form.category.data = get_detail.category
    form.edition.data = get_detail.edition
    form.remarks.data = get_detail.remarks
    form.language.data = get_detail.language

    return render_template(
        "publication/edit_publication.html",
        title="Edit Publication",
        form=form,
        get_detail=get_detail,
        pg=pg,
    )


@app.route("/publication_delete/<int:id>")
@login_required
def publication_delete(id):
    publication = Libcollection.query.get_or_404(id)
    try:
        db.session.delete(publication)
        db.session.commit()
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/publication/")
        os.remove(f"{upload_path}/{publication.image}")
        flash(f"Publication deleted", category="info")
        return redirect(url_for("publications", page_num="1"))
    except Exception as E:
        flash(f"Cannot delete Publicatin!!!", category="danger")
        return redirect(url_for("publications", page_num="1"))


# collector delete function, will not delete if any collector has data entered in any collection
@app.route("/librarydelete/<int:id>")
@login_required
def librarydelete(id):
    library = Library.query.get_or_404(id)
    try:
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/images/library/")
        os.remove(f"{upload_path}/{library.image}")
        db.session.delete(library)
        db.session.commit()

        flash(f"Library Deleted.", category="info")
        return redirect(url_for("add_library"))
    except Exception as E:
        flash(f"Cannot delete Library !!!", category="danger")
        return redirect(url_for("add_library"))


@app.route("/edit_library/<int:id>", methods=["POST", "GET"])
@login_required
def edit_library(id):
    form = AddLibrary()
    library = Library.query.get_or_404(id)
    upload_path = os.path.abspath(os.getcwd() + "/nml/static/images/library/")

    if request.method == "POST":
        # library = Library.query.get_or_404(id)

        if form.address.data == "":
            address = None
        else:
            address = form.address.data

        if form.contact.data == "":
            contact = None
        else:
            contact = form.contact.data

        if form.email.data == "":
            email = None
        else:
            email = form.email.data

        if form.hours.data == "":
            hours = None
        else:
            hours = form.hours.data

        if form.librarian.data == "":
            librarian = None
        else:
            librarian = form.librarian.data

        if form.libraryname.data == "":
            name = None
        else:
            name = form.libraryname.data

        if form.map_coordinates.data == "":
            map_coordinates = None
        else:
            map_coordinates = form.map_coordinates.data

        if form.website.data == "":
            website = None
        else:
            website = form.website.data

        library.address = address
        library.contact = contact
        library.email = email
        library.hours = hours
        library.librarian = librarian
        library.name = name
        library.map_coordinates = map_coordinates
        library.website = website

        if request.files["image"]:
            file = request.files["image"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)
            library.image = library.image
            file.save(f"{upload_path}/{library.image}")

        db.session.commit()
        return redirect(url_for("add_library"))

    form.address.data = library.address
    form.contact.data = library.contact
    form.email.data = library.email
    form.hours.data = library.hours
    form.librarian.data = library.librarian
    form.libraryname.data = library.name
    form.map_coordinates.data = library.map_coordinates
    form.website.data = library.website

    return render_template(
        "publication/edit_library.html",
        title="Edit Library",
        form=form,
        library=library,
    )


@app.route("/add_publication", methods=["GET", "POST"])
@login_required
def add_publication():
    form = AddPublication()
    # get_all_author = get_all(Author)
    # get_all_publishers = get_all(Publisher)
    # get_all_editor = get_all(Editor)
    # get_all_category = get_all(Category)
    get_all_language = get_all(Language)
    # get_all_language=Language.query.order_by(Language.name.asc())
    get_all_libraries = get_all(Library)
    # get_all_libraries = Library.query.order_by(Library.name.asc())
    get_latest = Libcollection.query.order_by(Libcollection.id.desc()).first()
    
    next_entry_id = get_latest.id + 1

    upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/publication/")

    if get_all_language:
        form.language.choices = [(langs.id, langs.name) for langs in get_all_language]
        form.language.choices = [("0", "Choose Language")] + form.language.choices
    else:
        form.language.choices = [("0", "No Language")]

    if get_all_libraries:
        form.library.choices = [
            (library.id, library.name) for library in get_all_libraries
        ]
        form.library.choices = [("0", "Choose Library")] + form.library.choices
    else:
        form.library.choices = [("0", "No Library")]
        
    if request.method == "POST":
        sub = Libcollection(
            title=form.title.data,
            author=form.author.data,
            publisher=form.publisher.data,
            isbn=form.isbn.data,
            acnum=form.acnum.data,
            editor=form.editor.data,
            language_id=form.language.data,
            year=form.year.data,
            edition=form.edition.data,
            category=form.category.data,
            library_id=form.library.data,
            remarks=form.remarks.data,
        )
        if request.files["image"]:
            file = request.files["image"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)
            sub.image = str(next_entry_id) + "_" + form.library.data + file_extension
            file.save(f"{upload_path}/{sub.image}")

        db.session.add(sub)
        db.session.commit()
        flash("Publication Added.", category="success")
        return redirect(url_for("add_publication"))

    return render_template(
        "publication/add_publication.html", title="Add Publication", form=form
    )


# search page
@app.route("/pubsearch", methods=["GET", "POST"])
@app.route("/pubsearch", methods=["GET", "POST"])
@login_required
def pubsearch():
    form = SearchFormnew()
    search_term = ""
    search_results = []
    search_total = ""
    # print ("search started")
    if request.method == "POST":
        if form.search.data:
            search_term = form.search.data
        else:
            search_term = ""
        # print (search_term + "POST")
        search_results = (
            Libcollection.query.join(
                Library
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Library.activestate == True
                )  # Adjust the condition for enabled as needed
                & (
                    
       # search_results = (
            # Libcollection.query.filter(
                Libcollection.title.like("%{}%".format(search_term))
                | Libcollection.author.like("%{}".format(search_term))
                | Libcollection.publisher.like("%{}".format(search_term))
                | Libcollection.year.like("%{}".format(search_term))
                | Libcollection.isbn.like("%{}%".format(search_term))
            )
            .order_by(Libcollection.id.desc())
            .paginate(page=page, per_page=items_per_page, error_out=False)
        ))
        search_total = Libcollection.query.filter(
            Libcollection.title.like("%{}%".format(search_term))
            | Libcollection.author.like("%{}".format(search_term))
            | Libcollection.publisher.like("%{}".format(search_term))
            | Libcollection.year.like("%{}".format(search_term))
            | Libcollection.isbn.like("%{}%".format(search_term))
        ).count()
    elif request.method == "GET":
        if request.args.get("search_term"):
            search_term = request.args.get("search_term")
        else:
            search_term = ""
        # print (search_term + " GET")
        page = request.args.get("page_num", 1, type=int)
        per_page = request.args.get("per_page", items_per_page, type=int)
        search_results = (
            Libcollection.query.join(
                Library
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Library.activestate == True
                )  # Adjust the condition for enabled as needed
                
                & (
                    Libcollection.title.like("%{}%".format(search_term))
                | Libcollection.author.like("%{}".format(search_term))
                | Libcollection.publisher.like("%{}".format(search_term))
                | Libcollection.year.like("%{}".format(search_term))
                | Libcollection.isbn.like("%{}%".format(search_term))
                )
            )
            .order_by(Libcollection.id.desc())
            .paginate(page=page, per_page=items_per_page, error_out=False)
        )
        # search_results = (
        #     Libcollection.query.filter(
        #         Libcollection.title.like("%{}%".format(search_term))
        #         | Libcollection.author.like("%{}".format(search_term))
        #         | Libcollection.publisher.like("%{}".format(search_term))
        #         | Libcollection.year.like("%{}".format(search_term))
        #         | Libcollection.isbn.like("%{}%".format(search_term))
        #     )
        #     .order_by(Libcollection.id.desc())
        #     .paginate(page=page, per_page=items_per_page, error_out=False)
        # )
        search_total = Libcollection.query.filter(
            Libcollection.title.like("%{}%".format(search_term))
            | Libcollection.author.like("%{}".format(search_term))
            | Libcollection.publisher.like("%{}".format(search_term))
            | Libcollection.year.like("%{}".format(search_term))
            | Libcollection.isbn.like("%{}%".format(search_term))
        ).count()

    return render_template(
        "pubsearch.html",
        search_options=search_options,
        form=form,
        search_results=search_results,
        search_term=search_term,
        title="Search Results",
        search_total=search_total,
    )

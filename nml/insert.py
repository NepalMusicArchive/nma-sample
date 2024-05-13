from flask import render_template, url_for, redirect, flash, request, jsonify

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

from nml.actions import *

now = datetime.now()
# add new collectin item page


@app.route("/assets", methods=["GET", "POST"])
@login_required
def assets():
    form = AddCollection()
    # get_all_contributors = get_all(Collectors)
    get_all_contributors = Collectors.query.order_by(Collectors.collector.asc())
    get_all_media = get_all(Media)
    get_all_companies = get_all(Company)
    get_all_languages = get_all(Language)
    get_all_genre = get_all(Genre)
    # print(get_all_genre)
    upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/")
    audio_upload_path = os.path.abspath(os.getcwd() + "/nml/static/music/")

    if get_all_contributors:
        form.contributor.choices = [
            (contrib.id, contrib.collector) for contrib in get_all_contributors
        ]
        form.contributor.choices = [
            ("0", "Choose Contributor")
        ] + form.contributor.choices
    else:
        form.contributor.choices = [("0", "No Contributor")]

    if get_all_genre:
        form.genre.choices = [(contrib.id, contrib.name) for contrib in get_all_genre]
        form.genre.choices = [("0", "Choose Genre")] + form.genre.choices
    else:
        form.genre.choices = [("0", "No Genre")]

    if get_all_languages:
        form.language.choices = [
            (contrib.id, contrib.name) for contrib in get_all_languages
        ]
        form.language.choices = [("0", "Choose Language")] + form.language.choices
    else:
        form.language.choices = [("0", "No Language")]

    # print(get_all_companies)
    if get_all_companies:
        form.company.choices = [
            (company.id, company.name) for company in get_all_companies
        ]
        form.company.choices = [("0", "Choose Company")] + form.company.choices
    else:
        form.company.choices = [("0", "No Company")]

    if get_all_media:
        form.media_name.choices = [
            (media_each.id, media_each.name) for media_each in get_all_media
        ]
        form.media_name.choices = [("0", "Choose Media Type")] + form.media_name.choices
    else:
        form.media_name.choices = [("0", "No Media")]

    ids = form.media_name.id
    get_filtered_formats = Format.query.filter_by(media_id="form.media_name.id").all()
    if get_filtered_formats:
        form.format_name.choices = [
            (each_format.id, each_format.name) for each_format in get_filtered_formats
        ]
    else:
        form.format_name.choices = [("0", "Select Media Type")]

    form.release_month.choices = [("", "Choose Release Month")] + [
        (x, calendar.month_name[x]) for x in range(1, 13)
    ]

    form.release_date.choices = [("", "Choose Release Date")] + [
        (x, x) for x in range(1, 32)
    ]

    form.release_year.choices = [("", "Choose Release Year")] + [
        (x, x) for x in range(1900, now.year + 1)
    ]

    show_details = (
        Collection.query.filter_by(user_id=current_user.id)
        .order_by(Collection.date_added.desc())
        .first()
    )

    if request.method == "POST":
        # print (form.inscriptions.data)
        if request.files["image"]:
            file = request.files["image"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)

        if request.files["image1"]:
            file = request.files["image1"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)
        
        if request.files["audiofile"]:
            filea = request.files["audiofile"]
            audioname = filea.filename
            file_name, file_extensiona = os.path.splitext(audioname)
           # print (file_namea, file_extension)
       # print (f'filename {audioname}')

        set_format_number = Format.query.filter_by(id=form.format_name.data).first()

        last_entry = Collection.query.order_by(Collection.id.desc()).first()

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

        if form.genre.data == "" or form.genre.data == "0":
            genre = "0"
        else:
            genre = form.genre.data

        if form.language.data == "" or form.language.data == "0":
            language = ""
        else:
            language = form.language.data

        if form.collection_title.data == "":
            title = None
        else:
            title = form.collection_title.data
        
        
        

        sub = Collection(
            collector_id=form.contributor.data,
            format_id=form.format_name.data,
            media_id=form.media_name.data,
            inscriptions=form.inscriptions.data,
            user_id=form.user_id.data,
            keywords=form.keywords.data,
            notes=form.notes.data,
            release_month=release_month,
            release_date=release_date,
            release_year=release_year,
            artist_id=form.artist.data,
            genre_id=genre,
            language_id=language,
            company_id=form.company.data,
            location=form.location.data,
            location1=form.location1.data,
            collection_title=title,
            activestate=1,
            date_added=datetime.utcnow(),
        )
        collector = Collectors.query.get(sub.collector_id)
        format = Format.query.get(sub.format_id)
        # print (format)
        tag_format = (format.name).replace(" ", "").lower()
        user = User.query.get(sub.user_id)
        if last_entry:
            next_entryid = last_entry.id + 1
        else:
            next_entryid = 1
        # Set the tagname attribute using details from the foreign key objects
        sub.tagname = f"nma-{collector.collectionid}-{tag_format}-{next_entryid}"
        if request.files["image"]:
            sub.image = sub.tagname + file_extension
            file.save(f"{upload_path}/{sub.image}")

        if request.files["image1"]:
            sub.image = sub.tagname + file_extension
            file.save(f"{upload_path}/{sub.image}")
            
        if request.files["audiofile"]:
            sub.audio_file = sub.tagname + file_extensiona
            filea.save(f"{audio_upload_path}/{sub.audio_file}")
        #print (file_extensiona, sub.audio_file)    

        db.session.add(sub)
        db.session.commit()

        flash(
            f'Collection added Successfully. Filename : <span class="user-select-all">{sub.tagname}</span>',
            category="success",
        )
        

        # session.query(ObjectRes).order_by(ObjectRes.id.desc()).first()
        return redirect(url_for("assets"))

    if show_details:
        default_month = get_default_month(show_details.id)
        default_year = get_default_year(show_details.id)
        default_contributor = get_default_contributor(show_details.id)
        default_media = get_default_media(show_details.id)
        default_format = get_default_format(show_details.id)
        default_company = get_default_company(show_details.id)
        # default_genre = get_default_genre(show_details.id)
        # default_language = get_default_languagem(show_details.id)
        # form.company.default=default_company
        form.contributor.default = default_contributor
        form.media_name.default = default_media
        form.release_month.default = default_month
        form.release_year.default = default_year
        get_filtered_formats = Format.query.filter_by(media_id=default_media).all()

        if get_filtered_formats:
            form.format_name.choices = [
                (each_format.id, each_format.name)
                for each_format in get_filtered_formats
            ]
        form.process()

    # print (show_details)
   
    return render_template("assets.html", title="Add Collection", form=form)


# listing of all collections, pagination enabled, variables set in environment
@app.route("/collections/<int:page_num>", methods=["GET", "POST"])
@login_required
def collections(page_num):
    form = AddCollection()
    # show_details = Collection.query.order_by(Collection.id.desc()).paginate(
    # #   per_page=items_per_page, page=page_num, error_out=True)

    if current_user.is_authenticated:
        show_details = (
            Collection.query.join(Collectors)
            .order_by(Collection.id.desc())
            .paginate(per_page=items_per_page, page=page_num, error_out=True)
        )

        total = Collection.query.join(Collectors).order_by(Collection.id.desc()).count()
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
    else:
        show_details = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (Collection.activestate == True)
            )
            .order_by(Collection.id.desc())
            .paginate(per_page=items_per_page, page=page_num, error_out=True)
        )
        total = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (Collection.activestate == True)
            )
            .count()
        )
        

    # show_details = Collection.query.filter_by(enabled="True").order_by(Collection.id.desc()).paginate(
    #     per_page=items_per_page, page=page_num, error_out=True)
    # contributors = get_all(Collectors)
    contributors = Collectors.query.order_by(Collectors.collector.asc())
    

    get_all_media = get_all(Media)

    return render_template(
        "collections.html",
        search_options=search_options,
        title="Collections Detail",
        show_details=show_details,
        form=form,
        records_pp=records_per_page,
        get_count=total,
        page=page_num,
        totald=totald,
    )


# collection delete function


@app.route("/collection_delete/<int:id>")
@login_required
def collection_delete(id):
    collectiond = Collection.query.get_or_404(id)
    # print (collectiond.image)
    try:
        db.session.delete(collectiond)
        db.session.commit()
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/")
        audio_path = os.path.abspath(os.getcwd() + "/nml/static/music/")
        
        if collectiond.image:           
            os.remove(f"{upload_path}/{collectiond.image}")
        
        if collectiond.audio_file:            
            os.remove(f"{audio_path}/{collectiond.audio_file}")

        flash(f"Collection deleted", category="info")
        return redirect(url_for("collections", page_num="1"))
    except Exception as E:
        # print (E)
        flash(f"Cannot delete Collection!!!", category="danger")
        return redirect(url_for("collections", page_num="1"))


# Collection Details page


@app.route("/collection/<int:id>/<int:pg>", methods=["GET", "POST"])
@login_required
def collection_detail(id, pg):
    get_detail = Collection.query.filter_by(id=id).first()
    if get_detail.image:
        filepath = url_for("static", filename="uploads/" + get_detail.image)
    else:
        mtype=get_detail.media.name
    # print (mtype)      
        if mtype=='Print':
            filepath=url_for("static", filename="/images/print.gif")
        elif mtype=='Audio':
            
            filepath=url_for("static", filename="/images/audio.gif")
        elif mtype=='Video':
            
            filepath=url_for("static", filename="/images/video.gif")
           # filepath = url_for("static", filename="/images/nma-logo_dim.png")
        
    audio_file = ""
    
    if get_detail.audio_file:
        
        audio_file = play_audio(get_detail.audio_file)
        # print (audio_file)

    # return 'found'
    
    
        
    return render_template(
        "collection_detail.html",
        title="Details",
        get_detail=get_detail,
        filepath=filepath,
        pg=pg,
        audio_file=audio_file,
    )


# Collection Edit page


@app.route("/editcol/<int:id>/<int:pg>", methods=["GET", "POST"])
@login_required
def edit_coll(id, pg):
    form = EditCollection()
    show_details = Collection.query.filter_by(id=id).first()
    # contributors = get_all(Collectors)
    contributors = Collectors.query.order_by(Collectors.collector.asc())
    get_all_media = get_all(Media)
    get_all_companies = get_all(Company)
    get_all_languages = get_all(Language)
    get_all_genre = get_all(Genre)
    # print (pg)
    # form = EditCollection()
    # get_detail = Collection.query.filter_by(id=id).first()
    default_month = get_default_month(id)
    default_date = get_default_date(id)
    default_year = get_default_year(id)
    default_contributor = get_default_contributor(id)
    default_media = get_default_media(id)
    default_format = get_default_format(id)
    default_company = get_default_company(id)
    default_genre = get_default_genre(id)
    default_language = get_default_languagem(id)
    form.release_month.default = default_month
    form.release_date.default = default_date
    form.release_year.default = default_year
    form.contributor.default = default_contributor
    form.company.default = default_company
    form.media_name.default = default_media
    form.genre.default = default_genre
    form.language.default = default_language
    form.format_name.default = default_format
    # print (default_date)
    # print(get_all_companies)

    if get_all_genre:
        form.genre.choices = [(contrib.id, contrib.name) for contrib in get_all_genre]
        form.genre.choices = [("0", "Choose Genre")] + form.genre.choices
    else:
        form.genre.choices = [("0", "No Genre")]

    if get_all_languages:
        form.language.choices = [
            (contrib.id, contrib.name) for contrib in get_all_languages
        ]
        form.language.choices = [("0", "Choose Language")] + form.language.choices
    else:
        form.language.choices = [("0", "No Language")]

    if get_all_companies:
        form.company.choices = [
            (company.id, company.name) for company in get_all_companies
        ]
        form.company.choices = [("0", "Choose Company")] + form.company.choices
    else:
        form.company.choices = [("0", "No Company")]
    # form.process()
    form.contributor.choices = [
        (contrib.id, contrib.collector) for contrib in contributors
    ]
    form.contributor.choices = [("", "Choose Contributor")] + form.contributor.choices

    form.media_name.choices = [(medias.id, medias.name) for medias in get_all_media]
    form.media_name.choices = [("", "Choose Media")] + form.media_name.choices

    get_filtered_formats = Format.query.filter_by(media_id=default_media).all()

    if get_filtered_formats:
        form.format_name.choices = [
            (each_format.id, each_format.name) for each_format in get_filtered_formats
        ]

    form.release_month.choices = [("", "Choose Release Month")] + [
        (x, calendar.month_name[x]) for x in range(1, 13)
    ]

    form.release_date.choices = [("", "Choose Release Date")] + [
        (x, x) for x in range(1, 32)
    ]

    form.release_year.choices = [("", "Choose Release Year")] + [
        (x, x) for x in range(1900, now.year + 1)
    ]
  
        
    if request.method == "POST":
        upload_path = os.path.abspath(os.getcwd() + "/nml/static/uploads/")
        audio_upload_path = os.path.abspath(os.getcwd() + "/nml/static/music/")
        company_info = Collection.query.get(id)
        
        if request.files["image"]:
            file = request.files["image"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)
            company_info.image = company_info.tagname + file_extension
            file.save(f"{upload_path}/{company_info.tagname+file_extension}")

        if request.files["image1"]:
            file = request.files["image1"]
            filename = file.filename
            file_name, file_extension = os.path.splitext(filename)
            company_info.image = company_info.tagname + file_extension
            file.save(f"{upload_path}/{company_info.tagname+file_extension}")
        
        if request.files["audiofile"]:
            filea = request.files["audiofile"]
            audioname = filea.filename
            file_namea, file_extensiona = os.path.splitext(audioname)
            # print (file_namea, file_extensiona)
            company_info.audio_file = company_info.tagname + file_extensiona
            filea.save(f"{audio_upload_path}/{company_info.tagname+file_extensiona}")
        #print (file_extensiona, sub.audio_file)   

        if form.release_month.data == "":
            release_month = None
        else:
            release_month = form.release_month.data

        if form.collection_title.data == "" or form.collection_title.data == "None":
            title = None
        else:
            title = form.collection_title.data

    
        if form.release_year.data == "":
            release_year = None
        else:
            release_year = form.release_year.data

        if form.release_date.data == "":
            release_date = None
        else:
            release_date = form.release_date.data

        if form.genre.data == "":
            genre = None
        else:
            genre = form.genre.data
            
        if form.language.data == "":
            language = None
        else:
            language = form.language.data

        if form.inscriptions.data:
            company_info.inscriptions = form.inscriptions.data
        else:
            company_info.inscriptions = company_info.inscriptions

        if form.keywords.data:
            company_info.keywords = form.keywords.data
        else:
            company_info.keywords = company_info.keywords

        if form.notes.data:
            company_info.notes = form.notes.data
        else:
            company_info.notes = company_info.notes

        company_info.language_id = language
        company_info.genre_id = genre
        company_info.collector_id = form.contributor.data
        company_info.media_id = form.media_name.data
        company_info.format_id = form.format_name.data
        company_info.company_id = form.company.data
        company_info.artist_id = form.artist.data
        company_info.tagname = f'nma-{company_info.collector.collectionid}-{company_info.formats.name.replace(" ","").lower()}-{company_info.id}'
        company_info.collection_title = title

        company_info.release_year = release_year

        company_info.release_month = release_month

        company_info.release_date = release_date
        company_info.location = form.location.data
        company_info.location1 = form.location1.data

        db.session.commit()
        return redirect(url_for("collections", page_num=pg))

    form.inscriptions.data = show_details.inscriptions
    form.keywords.data = show_details.keywords
    form.notes.data = show_details.notes
    audio_file = ""
    if show_details.audio_file:
        
        audio_file = play_audio(show_details.audio_file)

    return render_template(
        "edit_coll.html",
        title="Edit Collection Details",
        form=form,
        show_details=show_details,
        audio_file=audio_file,
    )


@app.route("/show_genre/", defaults={"id": 0}, methods=["POST", "GET"])
@app.route("/show_genre/<int:id>", methods=["POST", "GET"])
@login_required
def show_genre(id):
    form = AddGenre()
    show_details = Genre.query.all()
    if form.validate_on_submit():
        if id:
            filter = Genre.query.filter_by(id=id).first()
            filter.name = form.genre.data
            db.session.commit()
            flash(f"Genre Edited: {filter.name} ", category="success")
            return redirect(url_for("show_genre"))
            pass
        else:
            found = Genre.query.filter_by(name=form.genre.data).first()
            # print (found)

            if found:
                flash(f"Genre already exists: {form.genre.data} ", category="warning")
            else:
                genre_add = Genre(name=form.genre.data)
                db.session.add(genre_add)
                db.session.commit()
                flash(
                    f"Genre added successfully: {form.genre.data}", category="success"
                )
            return redirect(url_for("show_genre", page_num=1))
            pass
    else:
        if id:
            # Load the record data from the database and populate the form
            filter = Genre.query.filter_by(id=id).first()
            form.genre.data = filter.name
            id = filter.id
            pass
    return render_template(
        "add_genre.html",
        title="Genre List",
        show_details=show_details,
        form=form,
        id=id,
        search_options=search_options,
    )


# user delete function
@app.route("/genre_delete/<int:id>")
@login_required
def genre_delete(id):
    user = Genre.query.get_or_404(id)
    try:
        filter = Collection.query.filter_by(genre_id=id).first()
        if filter:
            flash(
                f"Cannot delete Genre!!! Some Collections have this genre ({user.name})",
                category="danger",
            )
            return redirect(url_for("show_genre", page_num="1"))
        else:
            # print('no')

            db.session.delete(user)
            db.session.commit()
            flash(f"Genre Deleted : {user.name} ", category="info")
            return redirect(url_for("show_genre", page_num="1"))

    except Exception as E:
        flash(f"Cannot delete Genre!!!", category="danger")
        return redirect(url_for("show_genre", page_num="1"))

# listing of all collections, pagination enabled, variables set in environment
@app.route("/collections/dataentry/", defaults={"page_num": 1}, methods=["POST", "GET"])
@app.route("/collections/dataentry/<int:page_num>", methods=["GET", "POST"])
# @login_required
def dataentry(page_num):
    form = AddCollection()
    # show_details = Collection.query.order_by(Collection.id.desc()).paginate(
    # #   per_page=items_per_page, page=page_num, error_out=True)

    if current_user.is_authenticated:
        show_details = (
            Collection.query.join(Collectors)
            .order_by(Collection.id.desc())
            .paginate(per_page=items_per_page, page=page_num, error_out=True)
        )

        total = Collection.query.join(Collectors).order_by(Collection.id.desc()).count()
    else:
        show_details = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (Collection.activestate == True)
            )
            .order_by(Collection.id.desc())
            .paginate(per_page=items_per_page, page=page_num, error_out=True)
        )
        total = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                (
                    Collectors.activestate == True
                )  # Adjust the condition for enabled as needed
                & (Collection.activestate == True)
            )
            .count()
        )

    # show_details = Collection.query.filter_by(enabled="True").order_by(Collection.id.desc()).paginate(
    #     per_page=items_per_page, page=page_num, error_out=True)
    # contributors = get_all(Collectors)
    contributors = Collectors.query.order_by(Collectors.collector.asc())


    get_all_media = get_all(Media)

    return render_template(
        "dataentry.html",
        search_options=search_options,
        title="Collections Detail",
        show_details=show_details,
        form=form,
        get_count=total,
        page=page_num,
    )


# listing of all collections, pagination enabled, variables set in environment
@app.route("/collections/missing/", defaults={"page_num": 1}, methods=["POST", "GET"])
@app.route("/collections/missing/<int:page_num>", methods=["GET", "POST"])
# @login_required
def missing(page_num):
    form = AddCollection()
    # show_details = Collection.query.order_by(Collection.id.desc()).paginate(
    # #   per_page=items_per_page, page=page_num, error_out=True)

    if current_user.is_authenticated:

        total = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                Collection.image == None
            )
            .count()
        )
        
        show_details = (Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                 
                    Collection.image == None
            )
            .order_by(Collection.id.desc())
            .paginate(page=1, per_page=total, error_out=False)
        )
        
        
    else:
        total = (
            Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
            .filter(
                Collection.image == None
            )
            .count()
        )
        
        show_details = (Collection.query.join(
                Collectors
            )  # Assuming there's a relationship between Collection and Collector
             .filter(
                
                    
                    Collection.image == None
            
                
            )
            .order_by(Collection.id.desc())
            .paginate(page=1, per_page=total, error_out=False)
          
        )
        
    # show_details = Collection.query.filter_by(enabled="True").order_by(Collection.id.desc()).paginate(
    #     per_page=items_per_page, page=page_num, error_out=True)
    # contributors = get_all(Collectors)
    contributors = Collectors.query.order_by(Collectors.collector.asc())


    get_all_media = get_all(Media)

    return render_template(
        "missing.html",
        search_options=search_options,
        title="Records Missing Images",
        show_details=show_details,
        form=form,
        get_count=total,
        page=page_num,
    )



# Collection Details page


@app.route("/collection/dataentry_detail/<int:id>/<int:pg>", methods=["GET", "POST"])
# @login_required
def dataentry_detail(id, pg):
    get_detail = Collection.query.filter_by(id=id).first()
    if get_detail.image:
        filepath = url_for("static", filename="uploads/" + get_detail.image)
    else:
        filepath = ""
    audio_file = ""
    
    if get_detail.audio_file:
        
        audio_file = play_audio(get_detail.audio_file)
        # print (audio_file)

    # return 'found'
    return render_template(
        "dataentry_detail.html",
        title="Details",
        get_detail=get_detail,
        filepath=filepath,
        pg=pg,
        audio_file=audio_file,
    )
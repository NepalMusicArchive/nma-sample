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
from datetime import datetime
import requests
from geopy.distance import geodesic

import socket



@app.route('/allcollection')
@login_required
def allcollection():
    query_details="All Collections"
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
            .count())
    return render_template('list_collections.html',get_totals=total,totald=totald,query_details=query_details)




@app.route('/collectiontest', methods=['GET'])
@login_required
def get_collections():
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)


    # Get search keyword from DataTables
    search_value = request.args.get('search[value]', type=str)
    
    # Base query without filtering
    base_query = Collection.query.join(Collection.collector).order_by(Collection.id.desc())
    base_query = base_query.join(Collection.media)
    base_query = base_query.join(Collection.formats)
    base_query = base_query.join(Collection.user)

    # Apply filtering if search keyword is provided
    if search_value:
        base_query = base_query.filter(
            or_(
               
                Collection.keywords.ilike(f"%{search_value}%"),
                Collection.inscriptions.ilike(f"%{search_value}%"),
                Collection.tagname.ilike(f"%{search_value}%"),
                Collection.notes.ilike(f"%{search_value}%"),
                Collection.collection_title.ilike(f"%{search_value}%"),             
                Collection.inscriptions.ilike(f"%{search_value}%"),
                Collection.keywords.ilike(f"%{search_value}%"),
                Collectors.collector.ilike(f"%{search_value}%"),
                Media.name.ilike(f"%{search_value}%"),
                Format.name.ilike(f"%{search_value}%"),
                User.fullname.ilike(f"%{search_value}%"),
                # Add other columns as needed for filtering
                
            )
        )

    # Get total records count (without pagination and filtering)
    total_records = base_query.count()

    # Apply pagination
    collections = base_query.offset(start).limit(length).all()

    # Get filtered records count
    filtered_records = base_query.count()

    # # Query the database based on start and length parameters
    # collections = Collection.query.offset(start).limit(length).all()

    # # Get total records count (without pagination)
    # total_records = Collection.query.count()

    # Prepare the response data in the required format
    data = []
    for collection in collections:
        
        data.append({
            
            'collector': collection.collector.collector,
            'id': collection.id,
            'user': collection.user.fullname,
            'media': collection.media.name,
            'format': collection.formats.name,
            'title': collection.collection_title,
            'inscriptions': collection.inscriptions,
            'tagname': collection.tagname,
            'collection_detail_url': url_for('collection_detail', id=collection.id,pg=1),
            
            'edit_url': url_for('edit_coll',id=collection.id,pg=1),
            'activate_url': url_for('active_inactivec'),
            'delete_url': url_for('collection_delete',id=collection.id),
            'item_state': collection.activestate,

            
            })

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    }

    return jsonify(response)


@app.route("/listbyformat/<keys>", methods=["GET", "POST"])
@login_required
def listbyformat(keys):
    q = keys
    per_page = items_per_page
    # get_data=Collection.query.paginate(per_page=10 ,page=page_num, error_out=True).filter(Collection.keywords.like('%'+ q +'%'))
    get_data = (
        Collection.query.filter(Collection.format_id == q)
        .order_by(Collection.id.desc())
    )
    query_details = Collection.query.filter(Collection.format_id == q).all()
    get_totals = Collection.query.filter(Collection.format_id == q).count()
    search_string = query_details[0].formats.name
    totald=0
    return render_template(
        f"list_collections.html",
        get_totals=get_totals,
        query_details=search_string,
        search_options=search_options,
        get_data=get_data,
        # page=page_num,
        q=q,
        totald=totald,
        get_formatname=query_details,
        title="Search Results",
    )


@app.route('/collectionbyformat/<keys>', methods=['GET'])
@login_required
def collectionbyformat(keys):
    q=keys
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)


    # Get search keyword from DataTables
    search_value = request.args.get('search[value]', type=str)
    
    # Base query without filtering
    base_query = Collection.query.filter(Collection.format_id == q).order_by(Collection.id.desc())

    # Apply filtering if search keyword is provided
    if search_value:
        base_query = base_query.filter(
            or_(
               
                Collection.keywords.ilike(f"%{search_value}%"),
                Collection.inscriptions.ilike(f"%{search_value}%"),
                Collection.tagname.ilike(f"%{search_value}%"),
                Collection.notes.ilike(f"%{search_value}%"),
                Collection.collection_title.ilike(f"%{search_value}%"),             
                Collection.inscriptions.ilike(f"%{search_value}%"),
                Collection.keywords.ilike(f"%{search_value}%"),
                # Add other columns as needed for filtering
                
            )
        )

    # Get total records count (without pagination and filtering)
    total_records = base_query.count()

    # Apply pagination
    collections = base_query.offset(start).limit(length).all()

    # Get filtered records count
    filtered_records = base_query.count()

    # # Query the database based on start and length parameters
    # collections = Collection.query.offset(start).limit(length).all()

    # # Get total records count (without pagination)
    # total_records = Collection.query.count()

    # Prepare the response data in the required format
    data = []
    for collection in collections:
        
        data.append({
            
            'collector': collection.collector.collector,
            'id': collection.id,
            'user': collection.user.fullname,
            'media': collection.media.name,
            'format': collection.formats.name,
            'title': collection.collection_title,
            'inscriptions': collection.inscriptions,
            'tagname': collection.tagname,
            'collection_detail_url': url_for('collection_detail', id=collection.id,pg=1),
            'edit_url': url_for('edit_coll',id=collection.id,pg=1),
            'activate_url': url_for('active_inactivec'),
            'delete_url': url_for('collection_delete',id=collection.id),
            'item_state': collection.activestate,

            
            })

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    }

    return jsonify(response)


#==================

@app.route('/get_timeline', methods=['GET'])
@login_required
def get_timeline():
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)


    # Get search keyword from DataTables
    search_value = request.args.get('search[value]', type=str)
    
    # Base query without filtering
    base_query = Timeline.query.order_by(Timeline.release_year.desc())

    # Apply filtering if search keyword is provided
    if search_value:
        base_query = base_query.filter(
            or_(
               
                Timeline.title.ilike(f"%{search_value}%"),
                Timeline.description.ilike(f"%{search_value}%"),
                Timeline.group.ilike(f"%{search_value}%"),
               
                # Add other columns as needed for filtering
                
            )
        )

    # Get total records count (without pagination and filtering)
    total_records = base_query.count()

    # Apply pagination
    results = base_query.offset(start).limit(length).all()

    # Get filtered records count
    filtered_records = base_query.count()

    # # Query the database based on start and length parameters
    # collections = Collection.query.offset(start).limit(length).all()

    # # Get total records count (without pagination)
    # total_records = Collection.query.count()

    # Prepare the response data in the required format
    data = []
    for res in results:
        
        data.append({
            'title': res.title,
            'description': res.description,
            'releasedate': res.release_date,
            'group': res.group,
            'edit_url': url_for('edit_event',id=res.id,pg=1),
            'delete_url': url_for('event_delete',id=res.id),
            })

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    }

    return jsonify(response)


#==================


@app.route('/allpublications')
@login_required
def allpublications():
    query_details="All Publications"
    totald=1
    if current_user.is_authenticated:
        show_details = Libcollection.query.order_by(Libcollection.id.desc())
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
    # print (total)
    return render_template('publication/list_publications.html',show_details=show_details,
        get_count=total,
        search_options=search_options,rtype="all",search_string="All Publications")


@app.route('/get_publications', methods=['GET'])
@login_required
def get_publications():
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)


    # Get search keyword from DataTables

    search_value = request.args.get('search[value]', type=str)
    
    # Base query without filtering
    base_query = Libcollection.query.order_by(Libcollection.id.desc())
    base_query = base_query.join(Libcollection.library)
    base_query = base_query.join(Libcollection.language)

    # Apply filtering if search keyword is provided
    if search_value:
        base_query = base_query.filter(
            or_(
               
                Libcollection.title.ilike(f"%{search_value}%"),
                Libcollection.author.ilike(f"%{search_value}%"),
                Libcollection.publisher.ilike(f"%{search_value}%"),
                Libcollection.isbn.ilike(f"%{search_value}%"),             
                Libcollection.acnum.ilike(f"%{search_value}%"),
                Libcollection.editor.ilike(f"%{search_value}%"),
                Libcollection.category.ilike(f"%{search_value}%"),
                Libcollection.year.ilike(f"%{search_value}%"),
                Libcollection.remarks.ilike(f"%{search_value}%"),
                Language.name.ilike(f"%{search_value}%"),
                Library.name.ilike(f"%{search_value}%"),
                # Add other columns as needed for filtering
                
            )
        )

    # Get total records count (without pagination and filtering)
    total_records = base_query.count()
    

    # Apply pagination
    publications = base_query.offset(start).limit(length).all()

    # Get filtered records count
    filtered_records = base_query.count()

    # # Query the database based on start and length parameters
    collections = Collection.query.offset(start).limit(length).all()

    
    # Prepare the response data in the required format
    data = []
    for publication in publications:
        
        data.append({
            
    
            
            'title': publication.title,
            'author': publication.author,
            'id': publication.id,
            'publisher': publication.publisher,          
            'isbn': publication.isbn,
            'language': publication.language.name,
            'edition': publication.edition,
            'library': publication.library.name,
            'category': publication.category,
            'year': publication.year,
          
     
          
            'lib_image_url': url_for('static',filename='images/library/'+ publication.library.image),         
            'detail_url': url_for('publication_details', id=publication.id,pg=1),
            'edit_url': url_for('edit_publication',id=publication.id,pg=1),
            'delete_url': url_for('publication_delete',id=publication.id),
          
          
          

            })

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    }

    return jsonify(response)

# =====================================


@app.route('/libpublications/<keys>', methods=["GET", "POST"])
@login_required
def libpublications(keys):
    
    q=keys    
    
    show_details = Libcollection.query.filter(Libcollection.library_id == q)
        
    total =  Libcollection.query.filter(Libcollection.library_id == q).count()
    
    search_options = Libcollection.query.filter(Libcollection.library_id == q).first() 
    search_string = show_details[0].library.name
    # print (show_details)
    return render_template('publication/list_publications.html',show_details=show_details,
        get_count=total,
        search_options=search_options,rtype="filtered",q=keys,search_string=search_string)


@app.route('/lib_publications/<keys>', methods=['GET'])
@login_required
def lib_publications(keys):
    q=keys
    # print (f'testd {q}')
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)


    # Get search keyword from DataTables
    search_value = request.args.get('search[value]', type=str)
    
    # Base query without filtering
    base_query = Libcollection.query.filter(Libcollection.library_id == q)
    base_query = base_query.join(Libcollection.language)

    # Apply filtering if search keyword is provided
    if search_value:
        base_query = base_query.filter(
            or_(
               
                Libcollection.title.ilike(f"%{search_value}%"),
                Libcollection.author.ilike(f"%{search_value}%"),
                Libcollection.publisher.ilike(f"%{search_value}%"),
                Libcollection.isbn.ilike(f"%{search_value}%"),             
                Libcollection.acnum.ilike(f"%{search_value}%"),
                Libcollection.editor.ilike(f"%{search_value}%"),
                Libcollection.category.ilike(f"%{search_value}%"),
                Libcollection.year.ilike(f"%{search_value}%"),
                Libcollection.remarks.ilike(f"%{search_value}%"),
                # Language.name.ilike(f"%{search_value}%"),
                Library.name.ilike(f"%{search_value}%"),
                # Add other columns as needed for filtering
                
            )
        )

    # Get total records count (without pagination and filtering)
    total_records = base_query.count()

    # Apply pagination
    publications = base_query.offset(start).limit(length).all()

    # Get filtered records count
    filtered_records = base_query.count()

    # # Query the database based on start and length parameters
    # collections = Collection.query.offset(start).limit(length).all()

    # # Get total records count (without pagination)
    # total_records = Collection.query.count()

    # Prepare the response data in the required format
    data = []
    for publication in publications:
        
        data.append({
            
    
            
            'title': publication.title,
            'author': publication.author,
            'id': publication.id,
            'publisher': publication.publisher,          
            'isbn': publication.isbn,
            'language': publication.language.name,
            'edition': publication.edition,
            'library': publication.library.name,
            'category': publication.category,
            'year': publication.year,
          
     
          
            'lib_image_url': url_for('static',filename='images/library/'+ publication.library.image),         
            'detail_url': url_for('publication_details', id=publication.id,pg=1),
            'edit_url': url_for('edit_publication',id=publication.id,pg=1),
            'delete_url': url_for('publication_delete',id=publication.id),
          
          
          

            })

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    }

    return jsonify(response)


# ===========================================

@app.route(
    "/listbycollector/<int:contributor_id>/<int:format_id>",
    methods=["GET", "POST"],
)
@login_required
def listbycollector(contributor_id, format_id):
    q = contributor_id
    format_id = format_id

    per_page = items_per_page
    if format_id == 0:
        get_data = (
            Collection.query.filter(Collection.collector_id == q)
            .order_by(Collection.id.desc())
            
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
    # test =
    # get_formatname = Collection.query.filter(
    #     Collection.collector_id == q).all()
    search_string = Collectors.query.filter(Collectors.id == q).first()

    return render_template(
        f"list_collectors.html",
        get_totals=get_totals,
        query_details=search_string,
        search_options=search_options,
        get_data=get_data,
        get_s=get_formatname,
        q=q,format_id=format_id,
        totald=totald,
        
        title="Search Results",
    )


@app.route('/collectionbycollector/<int:contributor_id>/<int:format_id>', methods=['GET'])
@login_required
def collectionbycollector(contributor_id,format_id):
    q=contributor_id
    format_id=format_id
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)


    # Get search keyword from DataTables
    search_value = request.args.get('search[value]', type=str)
    
    # Base query without filtering
    base_query = Collection.query.filter(Collection.collector_id == q).order_by(Collection.id.desc())
    if (format_id != 0 ):
        base_query = base_query.filter(Collection.format_id == format_id).order_by(Collection.id.desc())
    

    # Apply filtering if search keyword is provided
    if search_value:
        base_query = base_query.filter(
            or_(
               
                Collection.keywords.ilike(f"%{search_value}%"),
                Collection.inscriptions.ilike(f"%{search_value}%"),
                Collection.tagname.ilike(f"%{search_value}%"),
                Collection.notes.ilike(f"%{search_value}%"),
                Collection.collection_title.ilike(f"%{search_value}%"),             
                Collection.inscriptions.ilike(f"%{search_value}%"),
                Collection.keywords.ilike(f"%{search_value}%"),
                # Add other columns as needed for filtering
                
            )
        )

    # Get total records count (without pagination and filtering)
    total_records = base_query.count()

    # Apply pagination
    collections = base_query.offset(start).limit(length).all()

    # Get filtered records count
    filtered_records = base_query.count()

    # # Query the database based on start and length parameters
    # collections = Collection.query.offset(start).limit(length).all()

    # # Get total records count (without pagination)
    # total_records = Collection.query.count()

    # Prepare the response data in the required format
    data = []
    for collection in collections:
        
        data.append({
            
            'collector': collection.collector.collector,
            'id': collection.id,
            'user': collection.user.fullname,
            'media': collection.media.name,
            'format': collection.formats.name,
            'title': collection.collection_title,
            'inscriptions': collection.inscriptions,
            'tagname': collection.tagname,
            'collection_detail_url': url_for('collection_detail', id=collection.id,pg=1),
            'edit_url': url_for('edit_coll',id=collection.id,pg=1),
            'activate_url': url_for('active_inactivec'),
            'delete_url': url_for('collection_delete',id=collection.id),
            'item_state': collection.activestate,

            
            })

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    }

    return jsonify(response)
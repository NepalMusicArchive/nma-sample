from flask import redirect, url_for, flash
from nml import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from flask_migrate import Migrate


# function to get count(*) from specified table


def get_count(table):
    return table.query.count()


# function to get * from specified table


def get_all(table):
    # return table.query.all()
    return table.query.order_by(table.name.asc())


# db.session.query(Table).order_by(Table.column_name.asc()).all()

# default flask_login function to get user details


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# default flask_login function to check for sessions


@login_manager.unauthorized_handler
def unauthorized():
    flash(
        "You need to be registered to use this library. <br> Please contact the admin to get your account set up.",
        category="danger",
    )
    return redirect(url_for("login"))


# Users Table model


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    fullname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean(), nullable=False)
    db_notify = db.Column(db.Boolean(), nullable=False)
    activestate = db.Column(db.Boolean(), default=False)
    last_active = db.Column(db.DateTime, default=datetime.utcnow())
    login_state = db.Column(db.Boolean(), nullable=False, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f'{self.username} : {self.email} : {self.is_admin} : {self.db_notify} : {self.activestate} : {self.last_active} : {self.date_created.strftime("%d/%m/%Y,%H:%M:%S")}'


# Contributors Table model


class Collectors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collector = db.Column(db.String(60), nullable=False)
    collectionid = db.Column(db.String(5), nullable=False)
    activestate = db.Column(db.Integer, nullable=False, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    address = db.Column(db.String(250))
    email = db.Column(db.String(180))
    phone = db.Column(db.String(56))
    mobile = db.Column(db.String(56))
    seccontact = db.Column(db.String(16))
    relation = db.Column(db.String(16))
    secphone = db.Column(db.String(16))
    reference = db.Column(db.String(16))
    agreement = db.Column(db.Integer, default=True)
    remarks = db.Column(db.String(250))

    def __repr__(self):
        return f"<Collector: {self.collector} CollectionID: {self.collectionid}>"


# Media Table model


class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    formats = db.relationship("Format", backref="media", lazy=True)

    def __repr__(self):
        return f"{self.id} : {self.name} : {self.formats}"


# Format Table model


class Format(db.Model):
    __tablename__ = "format"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=False)

    def __repr__(self):
        return f"{self.id} : {self.name} : {self.media_id}"


# Recording Company Table model


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)

    def __repr__(self):
        return f"<Company: {self.name} : CompanyID: {self.id}>"


# Genre Company Table model


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)

    def __repr__(self):
        return f"<Genre: {self.name} : GenreID: {self.id}>"


# Collection Table model


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collector_id = db.Column(db.Integer, db.ForeignKey("collectors.id"), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=False)
    format_id = db.Column(db.Integer, db.ForeignKey("format.id"), nullable=False)
    collection_title = db.Column(db.String(100))
    inscriptions = db.Column(db.Text)
    keywords = db.Column(db.Text)
    notes = db.Column(db.Text)
    tagname = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    artist_id = db.Column(db.String(180))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=True)
    language_id = db.Column(db.Integer, db.ForeignKey("language.id"), nullable=False)
    release_month = db.Column(db.Integer, nullable=True)
    release_date = db.Column(db.Integer, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String(60))
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    activestate = db.Column(db.Integer, default=True)
    audio_file = db.Column(db.String(180))
    location = db.Column(db.String(150))
    location1 = db.Column(db.String(150))
    # artist=db.relationship(
    #     'Artist', backref=db.backref('collections', lazy=True))
    collector = db.relationship(
        "Collectors", backref=db.backref("collections", lazy=True)
    )
    company = db.relationship("Company", backref=db.backref("collections", lazy=True))
    genre = db.relationship("Genre", backref=db.backref("collections", lazy=True))
    language = db.relationship("Language", backref=db.backref("collections", lazy=True))
    formats = db.relationship("Format", backref=db.backref("collections", lazy=True))
    media = db.relationship("Media", backref=db.backref("collections", lazy=True))
    user = db.relationship("User", backref=db.backref("user", lazy=True))

    def __repr__(self):
        return f"{self.id} : {self.collector} : {self.user} : {self.media} : {self.formats} :  {self.company} : {self.genre} :  {self.language}: {self.inscriptions} : {self.image} :  {self.release_month}  :  {self.release_date}   :  {self.release_year} : {self.location} : {self.keywords} : {self.notes} : : {self.audio_file}"


# Timeline extras Table model
class Timeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    group = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text)
    release_month = db.Column(db.Integer, nullable=True)
    release_date = db.Column(db.Integer, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String(60))
    credit = db.Column(db.String(120))


# Library Table model


class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(90), nullable=True)
    contact = db.Column(db.String(60), nullable=True)
    activestate = db.Column(db.Integer, default=True)
    librarian = db.Column(db.String(60), nullable=True)
    image = db.Column(db.String(60), nullable=True)
    map_coordinates = db.Column(db.String(60), nullable=True)
    gmaps_url = db.Column(db.String(250))
    email = db.Column(db.String(60), nullable=True)
    website = db.Column(db.String(60), nullable=True)
    hours = db.Column(db.String(60), nullable=True)

    def __repr__(self):
        return f"<Library: {self.name} : LibraryID: {self.id}>"


# Language Table model


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"<Language: {self.name} : LanguageID: {self.id}>"


# Artist Table model
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=True)

    def __repr__(self):
        return f"<Artist: {self.name} : ArtistID: {self.id}>"
    
# Author Table model
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=True)

    def __repr__(self):
        return f"<Author: {self.name} : AuthorID: {self.id}>"


# Artist Table model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=True)

    def __repr__(self):
        return f"<Category: {self.name} : CategoryID: {self.id}>"


# Artist Table model


class Editor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"<Editor: {self.name} : EditorID: {self.id}>"


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"<Publisher: {self.name} : PublisherID: {self.id}>"


class Libcollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    author = db.Column(db.String(180))
    publisher = db.Column(db.String(180))
    isbn = db.Column(db.String(180))
    acnum = db.Column(db.String(180))
    editor = db.Column(db.String(180))
    language_id = db.Column(db.Integer, db.ForeignKey("language.id"))
    year = db.Column(db.String(60))
    edition = db.Column(db.String(180))
    category = db.Column(db.String(180))
    library_id = db.Column(db.Integer, db.ForeignKey("library.id"))
    remarks = db.Column(db.String(250))
    language = db.relationship("Language", backref=db.backref("libcoll", lazy=True))
    library = db.relationship("Library", backref=db.backref("libcoll", lazy=True))
    image = db.Column(db.String(60))
    date_added = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"{self.id} : {self.title} : {self.author} : {self.publisher} : {self.isbn} :  {self.acnum} :  {self.editor} : {self.language_id} : {self.year} :  {self.edition}  :  {self.category}   :  {self.library_id} : {self.remarks} : {self.language} : {self.image} : {self.date_added}"

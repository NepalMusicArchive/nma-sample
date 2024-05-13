from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    RadioField,
    PasswordField,
    SelectField,
    HiddenField,
    FileField,
    MultipleFileField,

)
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired
from datetime import datetime


# form used for the top search
class SearchFormnew(FlaskForm):
    search = StringField("Search")
    submit = SubmitField("Submit")


# form used to register new users


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=10)]
    )
    email = StringField("Email-ID", validators=[DataRequired(), Email()])
    fullname = StringField(
        "Full Name", validators=[DataRequired(), Length(min=3, max=50)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=3, max=40)]
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    is_admin = BooleanField("Administrator")
    email_notify = BooleanField("Email Notify")

    submit = SubmitField("Register")


# form displayed on the login page


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=3, max=16)]
    )
    submit = SubmitField("Login")


# form used to edit user password in the users page


class ChangePassword(FlaskForm):
    fullname = StringField(
        "Full Name", validators=[DataRequired(), Length(min=3, max=50)]
    )
    password = PasswordField(
        "Password",
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[EqualTo("password")]
    )
    is_admin = BooleanField("Administrator")
    email_notify = BooleanField("Email Notify", default=False)
    activestate = BooleanField("User Inactive", default=False)
    submit = SubmitField("Update User")


# form used to add new contributors


class AddCollector(FlaskForm):
    collector = StringField(
        "Contributor Name", validators=[DataRequired(), Length(min=3, max=60)]
    )
    collectionid = StringField("Collection ID", validators=[DataRequired()])
    address = TextAreaField("Address")
    email = StringField("Email")
    phone = StringField("Home Phone")
    mobile = StringField("Mobile")
    seccontact = StringField("Secondary Contact")
    relation = StringField("Relation")
    secphone = StringField("Secondary Phone")
    reference = StringField("Reference")
    agreement = BooleanField("Agreement Status")
    remarks = TextAreaField("Remarks")
    submit = SubmitField("Add Collector")


# form used to add new company


class AddCompany(FlaskForm):
    company = StringField(
        "Record Company", validators=[DataRequired(), Length(min=2, max=120)]
    )
    submit = SubmitField("Add Company")


# form used to add new media


class AddMedia(FlaskForm):
    newmedia = StringField(
        "Add Media Type", validators=[DataRequired(), Length(min=2, max=20)]
    )


# form used to new formats


class AddFormat(FlaskForm):
    media = SelectField("Media Type")
    newformat = StringField(
        "New Format Type", validators=[DataRequired(), Length(min=2, max=20)]
    )


# form used to add language
class AddLanguage(FlaskForm):
    language = StringField(
        "Language", validators=[DataRequired(), Length(min=2, max=120)]
    )
    submit = SubmitField("Add Language")


# form used to add language
class AddGenre(FlaskForm):
    genre = StringField("Genre", validators=[DataRequired(), Length(min=2, max=120)])
    submit = SubmitField("Add Genre")


# form used to add new collection


class AddCollection(FlaskForm):
    now = datetime.now()
    contributor = SelectField("Contributor", validators=[DataRequired()])
    media_name = SelectField("Media", choices=[])
    format_name = SelectField("Format", choices=[])
    genre = SelectField("Genre", choices=[])
    language = SelectField("Language", choices=[])
    user_id = HiddenField("user_id")
    collection_title = StringField("Title", validators=[Length(min=4, max=100)])
    location = StringField("Location", validators=[Length(min=4, max=100)])
    location1 = StringField("Location", validators=[Length(min=4, max=100)])
    inscriptions = TextAreaField(
        "Inscriptions", description="Required Filed. minimum 10 letters"
    )
    image = FileField("Cover", render_kw={"accept": "image/png, image/jpeg"})
    image1 = FileField("Photo/Cover", render_kw={"accept": "image/png, image/jpeg"})
    audiofile = FileField("Media File", render_kw={"accept": "audio/mpeg, audio/wav, audio/x-m4a, video/mpeg, video/quicktime"})
    #, video/mp4, video/quicktime
    release_month = SelectField("Release Month", choices=[])
    release_date = SelectField("Release Date", choices=[])
    release_year = SelectField("Release Year", choices=[])
    artist = StringField("Artist")
    company = SelectField("Released By", choices=[])
    keywords = TextAreaField(
        "keywords",description="Keywords comma separated",
    )
    notes = TextAreaField("Remarks/Notes", description="Additional Notes")
    submit = SubmitField("Add Collection")


# form used to resume adding new collection


class AddNew(FlaskForm):
    now = datetime.now()
    contributor = SelectField("Contributor", validators=[DataRequired()])
    # collection_id=HiddenField('Collection_id')
    media_name = SelectField(
        "Media",
    )
    format_name = SelectField(
        "Format",
    )
    release_month = SelectField("Release Month", choices=[])
    release_date = SelectField("Release Date", choices=[])
    release_year = SelectField("Release Year", choices=[])
    collection_title = StringField("Title", validators=[Length(min=4, max=100)])
    image = FileField("Cover", render_kw={"accept": "image/png, image/jpeg"})
    inscriptions = TextAreaField(
        "Inscriptions", description="Required Filed. minimum 10 letters"
    )
    artist = StringField("Artist")
    company = SelectField("Released By", choices=[])
    keywords = TextAreaField("keywords", description="Keywords comma separated")
    notes = TextAreaField("Remarks/Notes", description="Additional Notes")
    submit = SubmitField("Add New Collection")


# form used to edit collection


class EditCollection(FlaskForm):
    now = datetime.now()
    contributor = SelectField("Contributor", validators=[DataRequired()])
    media_name = SelectField(
        "Media",
    )
    format_name = SelectField(
        "Format",
    )
    release_month = SelectField("Release Month", choices=[])
    release_date = SelectField("Release Date", choices=[])
    release_year = SelectField("Release Year", choices=[])
    genre = SelectField("Genre", choices=[])
    language = SelectField("Language", choices=[])
    collection_title = StringField("Title", validators=[Length(min=4, max=100)])
    image = FileField("Cover", render_kw={"accept": "image/png, image/jpeg"})
    image1 = FileField("Cover", render_kw={"accept": "image/png, image/jpeg"})
    inscriptions = TextAreaField(
        "Inscriptions", description="Required Filed. minimum 10 letters"
    )
    location = StringField("Location")
    location1 = StringField("Location")
    artist = StringField("Artist")
    company = SelectField("Released By", choices=[])
    keywords = TextAreaField("keywords", description="Keywords comma separated")
    notes = TextAreaField("Remarks/Notes", description="Additional Notes")
    audiofile = FileField("Media File", render_kw={"accept": "audio/mpeg, audio/wav, audio/x-m4a"})
    #, video/mp4, video/quicktime
    submit = SubmitField("Save")


class AddTimeline(FlaskForm):
    now = datetime.now()

    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=2, max=200)],
        description="Title",
    )
    description = TextAreaField(
        "Description",
        description="Additional Description",
        validators=[DataRequired(), Length(min=2, max=500)],
    )
    release_month = SelectField("Month", choices=[])
    release_date = SelectField("Date", choices=[])
    release_year = SelectField("Year", choices=[])
    image = FileField("Image", render_kw={"accept": "image/png, image/jpeg"})
    credit = StringField("Credit", validators=[Length(min=4, max=100)])
    group = SelectField("Group", validators=[DataRequired()])
    submit = SubmitField("Add Event")


# form used to add new company


class AddLibrary(FlaskForm):
    libraryname = StringField(
        "Library name", validators=[DataRequired(), Length(min=2, max=120)]
    )
    address = TextAreaField(
        "Address", validators=[DataRequired(), Length(min=2, max=120)]
    )
    contact = StringField(
        "Phone Number", validators=[DataRequired(), Length(min=2, max=120)]
    )
    librarian = StringField("Librarian", validators=[Length(min=2, max=120)])
    image = FileField("Logo (300px X 236px)", render_kw={"accept": "image/png, image/jpeg"})
    map_coordinates = StringField(
        "Map coordinates", validators=[Length(min=2, max=120)]
    )
    maps_url=StringField(
        "Map coordinates", validators=[Length(min=2, max=300)]
    )
    gmaps_url= StringField(
        "Google Map URL", validators=[Length(min=2, max=450)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    website = StringField(
        "Website", validators=[DataRequired(), Length(min=2, max=120)]
    )
    hours = StringField("Hours", validators=[DataRequired(), Length(min=2, max=120)])
    submit = SubmitField("Add Library")


class AddPublication(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=2, max=120)])

    author = StringField("Author", validators=[Length(min=2, max=120)])
    publisher = StringField("Publisher", validators=[Length(min=2, max=120)])

    isbn = StringField("ISBN", validators=[Length(min=2, max=120)])
    acnum = StringField("Accession Number", validators=[Length(min=2, max=120)])
    editor = StringField("Editor", validators=[Length(min=2, max=120)])
    language = SelectField("Language", choices=[])

    year = StringField("Year", validators=[Length(min=2, max=120)])
    edition = StringField("Edition")
    category = StringField(
        "Category", validators=[DataRequired(), Length(min=2, max=120)]
    )
    library = SelectField("Library", choices=[])
    remarks = TextAreaField("Remarks", validators=[Length(min=2, max=8000)])
    image = FileField("Cover", render_kw={"accept": "image/png, image/jpeg"})

    submit = SubmitField("Add New Publication")
    
    
class UploadForm(FlaskForm):
    files = FileField('Upload Files', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Only image files are allowed.')
    ])

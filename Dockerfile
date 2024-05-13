FROM python:3.9-alpine

LABEL "App.Vendor"="Nirat Sthapit"
LABEL "CREATED FOR"="Nepal Music Archive"
LABEL version="2.5"

WORKDIR /code

# copy required files for install python dependencies
COPY ./requirements.txt /code/requirements.txt
RUN apk --update-cache add sqlite ffmpeg\
    && rm -rf /var/cache/apk/* 
    # && chmod 755 ./init_db.sh \
    # && ./init_db.sh \
    # && chmod a+rw ./nml/nml.db \
    # && rm -f ./init_db.sh nml.sql
# start the app
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# copy over all code 
COPY . /code
# change working directory to code
WORKDIR /code


#enable these if using simple python
#EXPOSE 5000
#CMD ["python", "run.py"]

##enabled these if using gunicorn
EXPOSE 8000
CMD ["gunicorn", "run:app", "-b", "0.0.0.0:8000", "--log-level", "info"]



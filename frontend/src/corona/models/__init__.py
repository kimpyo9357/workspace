from flask_sqlalchemy import SQLAlchemy
from corona import app
from corona import config

app.config['SQLALCHEMY_DATABASE_URI'] = config.get_alchemy_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

from corona.models import LogTable
from corona.models import UploadedFile
from corona.models import InforTable

db.create_all()
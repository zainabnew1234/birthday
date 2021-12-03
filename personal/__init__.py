from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy  import SQLAlchemy
from flask_mail import Mail,Message
from flask_migrate import Migrate
import config



app = Flask(__name__,instance_relative_config=True)

csrf = CSRFProtect(app)
app.config.from_pyfile("config.py")
app.config.from_object(config.ProductionConfig)
mail=Mail(app)
db = SQLAlchemy(app)
migrate=Migrate(app,db)




from personal.routes import user_routes,admin_routes
from personal import models














from flask import Flask 
from rgz import rgz

app = Flask(__name__)

app.register_blueprint(rgz)

app.secret_key = "123"
user_db = "kristina_knowledge_base"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "rgz_web"
password = "123"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

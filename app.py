from flask import Flask, render_template, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from form import MyForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
# MySQL config

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://myuser:verificables@localhost/project_app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy object
db = SQLAlchemy(app)


class User(db.Model):
	rut = db.Column(db.String(10), primary_key=True)

class bienRaiz(db.Model):
	comuna = db.Column(db.Integer)
	manzana = db.Column(db.Integer)
	predio = db.Column(db.Integer)
	rol = db.Column(db.String(20), primary_key=True)

	def __init__(self, comuna, manzana, predio):
		self.comuna = comuna
		self.manzana = mazana
		self.predio = predio
		self.rol = f'{comuna}-{mazana}-{predio}'




@app.route('/')
def index():
	return 'Hello World!'

@app.route('/form', methods=['GET', 'POST'])
def form():
	form = MyForm()
	if form.validate_on_submit():
		# Here, you can process form data
		flash(f'Form submitted with name: {form.name.data}')

		# Transform to json



		return redirect('/')
	return render_template('form.html', title='Form', form=form)

if __name__ == '__main__':
	app.run(debug=True)


# docker run --name project -e MYSQL_ROOT_PASSWORD=verificables -e MYSQL_DATABASE=project_app_db -e MYSQL_USER=myuser -e MYSQL_PASSWORD=verificables -p 3306:3306 -d mysql
# docker exec -it project mysql -umyuser -pverificables

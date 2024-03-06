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
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(255))
	email = db.Column(db.String(255))

	def __repr__(self):
		return f"User('{self.username}')"


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

# using python 3
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from data import ACTORS
import stripe

app = Flask(__name__)
# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'some?bamboozle#string-foobar'
# Flask-Bootstrap requires this line
Bootstrap(app)
# this turns file-serving to static, using Bootstrap files installed in env
# instead of using a CDN
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

stripe_keys = {
  'secret_key': 'sk_test_51HevTDEdTRA1Rei30P0yeyx7IRA7Jr8NdcE5hGypfJ3Z3fNPlJzCdxnpavq2fcfmbpA9YpJhMjXGLtInl8UNcbuy00RVMX4sCF',
  'publishable_key': 'pk_test_51HevTDEdTRA1Rei3c76wSKc8hFjcEumOGFDTOsLgSKILa7jzv2xmy9sKZukoaypxeCLJh8Ubyp2lPQeHMJbUTZdi00Zjioxafj'
}

stripe.api_key = stripe_keys['secret_key']

# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NameForm(FlaskForm):
    name = StringField('What\'s your name?', validators=[Required()])
    partnersName = StringField('What\'s your partner\'s name?', validators=[Required()])
    cheaterName = StringField('What\'s of the person your partner is cheating with?', validators=[Required()])
    submit = SubmitField('Submit')

class CheckoutButton(FlaskForm):
    submit = SubmitField('Buy Another Story')
# define functions to be used by the routes

# retrieve all the names from the dataset and put them into a list
def get_names(source):
    names = []
    for row in source:
        name = row["name"]
        names.append(name)
    return sorted(names)

# find the row that matches the id in the URL, retrieve name and photo
def get_actor(source, id):
    for row in source:
        if id == str( row["id"] ):
            name = row["name"]
            photo = row["photo"]
            # change number to string
            id = str(id)
            # return these if id is valid
            return id, name, photo
    # return these if id is not valid - not a great solution, but simple
    return "Unknown", "Unknown", ""

# find the row that matches the name in the form and retrieve matching id
def get_id(source, name):
    for row in source:
        if name == row["name"]:
            id = row["id"]
            # change number to string
            id = str(id)
            # return id if name is valid
            return id
    # return these if id is not valid - not a great solution, but simple
    return "Unknown"

# all Flask routes below

# two decorators using the same function
@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    names = get_names(ACTORS)
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        return redirect( url_for('actor', id=form.name.data,
        partnersName=form.partnersName.data, cheaterName=form.cheaterName.data ) )
    return render_template('index.html', names=names, form=form, message=message)

@app.route('/name/<id>/<partnersName>/<cheaterName>/')
def actor(id, partnersName, cheaterName):
    form = CheckoutButton()
    story = "{name} walks into a room as they hear {partnersName} moan to {name} \
            surpise their best friend {cheaterName} was on top of {partnersName}".format(
                name=id, partnersName=partnersName, cheaterName=cheaterName
            )
    return render_template('free-story.html', story=story, form=form, key=stripe_keys['publishable_key'])

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# keep this as is
if __name__ == '__main__':
    app.run(debug=True)

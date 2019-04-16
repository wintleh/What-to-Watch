from flask import render_template
from app import app
from app.forms import ReccomendationForm

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = ReccomendationForm()
    show_title = str(form.show_title.data)

    if form.validate_on_submit():
        # Connection to the model, use to estimate the value
        result = '70' # Get this value from the model
        return render_template('index.html', form=form, show=show_title, result=result)
    return render_template('index.html', form=form)


# @app.route('/data')
# def data():
#     return render_template('data.html')

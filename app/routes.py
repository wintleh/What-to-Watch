from flask import render_template
from app import app
from app.forms import ReccomendationForm
from model import predict

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = ReccomendationForm()
    show_title = str(form.show_title.data)

    if form.validate_on_submit():
        prediction, actual, boolValue = predict(show_title)
        if(boolValue):
            return render_template('index.html', form=form, \
                show=show_title.title(), result=str(prediction[0]), \
                actual=actual)
        return render_template('index.html', form=form, err='Show not found')
    return render_template('index.html', form=form)


# @app.route('/data')
# def data():
#     return render_template('data.html')

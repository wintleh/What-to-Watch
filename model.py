import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels

main_model = None

#display method, from:
# https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html

def plot_confusion_matrix(y_true, y_pred, classes,
                          normalize=False,
                          title=None,
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
#     classes = classes[unique_labels((y_true)), (y_pred)))]
    #ME: disable above functionality for the PA
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    return ax


def predict(show_title):
    '''
    Give a prediction based on the name of the show
    '''
    model = get_model(main_model)

    show_title = re.sub(r'\W+', '_', show_title)    # Replace all non-alphanumeric chars with _
    show_title = re.sub('__*', '_', show_title)     # Shorten multiple underscores to only one

    df = index_fixed[index_fixed.loc[:, 'title'] == show_title]  # Should only get one row

    if(df.shape[0] == 1):
        # Get the actual audience rating
        actual = df.iloc[0, 4]

        # Drop all unnecessary columns
        df = df.drop(columns=['title', 'years', 'poster_link', \
            'audience_score','synopsis', 'creators', 'stars', 'network', \
            'premiere_date', 'genre', 'exec_producers'])

        return model.predict(df), actual, True
    return 'None', None, False


def get_model(model):
    '''
    Train and return the model
    '''
    if(model == None):
        X_train, X_test, y_train, y_test = train_test_split(test_only, y, random_state=42, train_size=0.7)

        model = MultinomialNB(alpha=0.9)
        model.fit(X_train, y_train)

        print("Train accuracy is %.2f %%" % (model.score(X_train, y_train)*100))
        print("Test accuracy is %.2f %%" % (model.score(X_test, y_test)*100))

        target_labels = ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']

        y_pred = model.predict(X_test)
        plot_confusion_matrix(y_test, y_pred, classes=target_labels, normalize=True,
                              title='Normalized confusion matrix for test data')
        plt.show()

    return model

    # scores = cross_val_score(model, test_only, y, cv=10)
    # print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    # print("Train accuracy is %.2f %%" % (model.score(X_train, y_train)*100))
    # print("Test accuracy is %.2f %%" % (model.score(X_test, y_test)*100))

    # target_labels = ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
    #
    # y_pred = model.predict(X_test)
    # plot_confusion_matrix(y_test, y_pred, classes=target_labels, normalize=True,
    #                       title='Normalized confusion matrix for test data')
    # plt.show()

################################################################################
# Read, clean, and vectorize data
################################################################################

data = pd.read_csv('.\\data\\tv_shows.csv', encoding='ISO-8859-1')
data = data.replace('', np.nan).replace('[]', np.nan).replace('|', ',')
data.dropna(subset=['critic_score', 'exec_producers', 'genre', 'stars'], inplace=True)

# Drop all rows where audience_score or critic_score is NaN
test_only = data.dropna(subset=['audience_score', 'critic_score', 'synopsis'])

# Round all scores to nearest ten
test_only.loc[:, 'critic_score'] = (test_only.loc[:, 'critic_score']/100).round(1) * 100
test_only.loc[:, 'audience_score'] = (test_only.loc[:, 'audience_score']/100).round(1) * 100

# Reset the index, based on the 'good' data
test_only = test_only.reset_index()

# Vectorize the stars
vect = CountVectorizer(encoding='ISO-8859-1', token_pattern=r"'(.*?)'")
vect_stars = vect.fit_transform(test_only.loc[:, 'stars'])
test_only = test_only.join(\
            pd.DataFrame(\
                        vect_stars.todense(),\
                        columns = vect.get_feature_names()\
                        ).iloc[:, 2:])      # Drop first few columns, not actual people

# Vectorize the creators
vect = CountVectorizer(encoding='ISO-8859-1', token_pattern=r"'(.*?)'")
vect_creators = vect.fit_transform(test_only.loc[:, 'creators'].values.astype('U'))
test_only = test_only.join(\
            pd.DataFrame(\
                        vect_creators.todense(),\
                        columns=vect.get_feature_names()),
            lsuffix='_s', rsuffix='_c')

# Vectorize the synopsis
vect = CountVectorizer(encoding='ISO-8859-1')
vect_synopsis = vect.fit_transform(test_only.loc[:, 'synopsis'])
transformer = TfidfTransformer().fit(vect_synopsis)
transformed_synopsis = transformer.transform(vect_synopsis)
test_only = test_only.join(pd.DataFrame(vect_creators.todense()))

y = test_only.loc[:, 'audience_score']

index_fixed = test_only

# Drop all unnecessary columns
test_only = test_only.drop(columns=['title', 'years', 'poster_link', \
    'audience_score','synopsis', 'creators', 'stars', 'network', \
    'premiere_date', 'genre', 'exec_producers'])
# test_only.to_csv('.\\data\\full.csv')

from flask import Flask, render_template, request
import pandas as pd
import pickle as pkl
import requests
import bz2
import random
import os
from config import Config


# decompress_pickle function
def decompress_pickle(file):

    data = bz2.BZ2File(file, 'rb')
    data = pkl.load(data)
    return data


# invoking the function
Similmodel = decompress_pickle('models/Similarity.pbz2')

# reading the movies dict
with open('models/movies_dict.pkl', 'rb') as f:
    movies_dict = pkl.load(f)


# reloading the similarity matrix
# with open('similarity.pkl', 'rb') as f:
#     similarity = pkl.loads(f.read())

# making the movie dataframe from movies dict
movie_df = pd.DataFrame(movies_dict)


# movies overviews, ratings etc function
def movie_overview(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=347c4eb6a4061bffcd128405326844d3&language=en-US'.format(movie_id))
    data = response.json()
    l = [data['overview'], data['vote_average'],
         data['genres'], data['release_date']]
    return l

# function for movie poster fetching


def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=347c4eb6a4061bffcd128405326844d3&language=en-US'.format(movie_id))

    data = response.json()
    return "https://image.tmdb.org/t/p/w500/"+data['poster_path']

# function for movies watch


def movie_download(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=347c4eb6a4061bffcd128405326844d3&language=en-US'.format(movie_id))
    data = response.json()
    return data['homepage']


def five_movie(movie_id):
    distances = Similmodel[movie_id]
    movie_list = sorted(list(enumerate(distances)),
                        reverse=True, key=lambda x: x[1])[1:6]

    url_movies = []

    for i in movie_list:
        movie_id = movie_df.iloc[i[0]].id
        url_movies.append(movie_download(movie_id))
    return url_movies

# making a recommended system function


def recommend(movie_id):
    try:
        # movie_index=movie_df[movie_df['title']==movie].index[0]
        distances = Similmodel[movie_id]
        movie_list = sorted(list(enumerate(distances)),
                            reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_poster = []
        for i in movie_list:
            movie_id = movie_df.iloc[i[0]].id

            recommended_movies.append(movie_df.iloc[i[0]].title)
            # fetch poster from api
            recommended_movies_poster.append(fetch_poster(movie_id))

        return recommended_movies_poster, recommended_movies
    except:
        print("something went wrong?")


# fetching image for selected movies
def select_poster(movie):

    # recommended_movies=[]
    recommended_movies_poster = []

    recommended_movies_poster.append(fetch_poster(
        movie_df[movie_df['title'] == movie].iloc[0].id))
    return recommended_movies_poster


# init the application
app = Flask(__name__)
app.config.from_object(Config)

@app.route('/', methods=['GET', 'POST'])
# home function
def home():
    ov = ""
    vt = ""
    release_dt = ""
    genrse_com = ""
    recommandation = ""
    recommend_img = ""
    sv_name = ""
    select_poster_img_str = ""
    movie_title = movie_df['title'].values
    selected_value = ""
    movie_top = movie_df['title'].head(12)
    movie_top_id = movie_df['id'].head(12)
    movie_img_link = []
    for i in movie_top_id:
        movie_img_link.append(fetch_poster(i))

    # print(movie_img_link)
    if request.method == 'POST':
        selected_value = request.form.get('movies-name')

    if selected_value.isdigit():
        sv = int(selected_value)
        sv_name = movie_df['title'].iloc[sv]
        m_id = movie_df['id'] .iloc[sv]
        print(m_id)
        ov, vt, genres, release_dt, = movie_overview(m_id)
        genrse_com = ""
        g = genres
        gd = dict(g)
        print(type(g), type(gd))
        c = 0
        for i in g:
            print(g[c]['name'])
            gc = g[c]['name']
            genrse_com += gc+","
            c += 1
            print(c)

        # selected_poster fateching
        sv_img = movie_df['id'] .iloc[sv]
        select_poster_img_str = fetch_poster(sv_img)
        # print(sv, "type: ", type(sv))
        recommend_img, recommandation = recommend(sv)
    else:
        pass

    mylist = zip(recommandation, recommend_img)

    movies_link_img = zip(movie_top, movie_img_link)

    context = {
        'movies_title': movie_title,
        'selected': sv_name,
        'red_img': recommend_img,
        'recommended': recommandation,
        'movie_top': movie_top,
        'mylist': mylist,
        'movie_img': movies_link_img,
        'select_img': select_poster_img_str,
        'overview': ov,
        'voting': vt,
        'genres': genrse_com,
        'rd': release_dt,
    }

    return render_template('index.html', **context)


if __name__ == '__main__':
    app.run()

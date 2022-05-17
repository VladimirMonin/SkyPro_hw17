import rating as rating
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)

    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")

    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres = GenreSchema(many=True)

api = Api(app)

movies_ns = api.namespace('movies')


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):

        director_id = request.args.get('director_id')
        movie_id = request.args.get('movie_id')
        genre_id = request.args.get('genre_id')
        page_num = request.args.get('page')

        select = db.session.query(Movie.id, Movie.title, Movie.description, Movie.trailer, Movie.year, Movie.rating,
                                  Genre.name, Director.name).join(Genre).join(Director)

        if director_id:
            select = select.filter(Movie.director_id == director_id)
        elif movie_id:
            select = select.filter(Movie.id == movie_id)
        elif genre_id:
            select = select.filter(Movie.genre_id == genre_id)
        elif page_num:
            limit = 5
            offset = (int(page_num) - 1) * 5
            select = select.limit(limit).offset(offset)

        result = select.all()

        return [{
            'title': title,
            'genre_name': genre_name,
            'director_name': director_name,
            'id': id,
            'description': description,
            'trailer': trailer,
            'year': year,
            'rating': rating

        } for id, title, description, trailer, year, rating, genre_name, director_name, in result], 200


if __name__ == '__main__':
    app.run(debug=True)

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

        global result # Не совсем понимаю, почему без глобализации нет возврата result. Хотя return находится ВНУТРИ ФУНКЦИИ

        director_id = request.args.get('director_id')
        movie_id = request.args.get('movie_id')
        genre_id = request.args.get('genre_id')
        page_num = request.args.get('page')

        if director_id:
            result = Movie.query.filter(Movie.director_id == director_id)

        elif movie_id:
            result = Movie.query.filter(Movie.id == movie_id)

        elif genre_id:
            result = Movie.query.filter(Movie.genre_id == genre_id)

        elif page_num:
            limit = 5
            offset = (int(page_num) - 1) * 5
            result = Movie.query.limit(limit).offset(offset)

        else:
            result = db.session.query(Movie).all()

        return movies_schema.dump(result), 200


if __name__ == '__main__':
    app.run(debug=True)

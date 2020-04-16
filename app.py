from flask import Flask, redirect, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func 
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMU_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

books_authors_table = db.Table('books_authors', db.Column('book_id', db.Integer, db.ForeignKey('books.id', ondelete = 'cascade'), primary_key = True), db.Column('author_id', db.Integer, db.ForeignKey('authors.id', ondelete = 'cascade'), primary_key = True))

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(45))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default = func.now())
    updated_at = db.Column(db.DateTime, server_default = func.now(), onupdate = func.now())
    book_authors = db.relationship('Author', secondary = books_authors_table)

    def book_id(self):
        return self.id

class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default = func.now())
    updated_at = db.Column(db.DateTime, server_default = func.now(), onupdate = func.now())
    author_of_books = db.relationship('Book', secondary = books_authors_table)

    def name(self):
        return self.first_name +" "+ self.last_name
    def author_id(self):
        return self.id        

@app.route("/")
def add_books():
    books = Book.query.all()
    return render_template("book.html", books = books)

@app.route("/authors")
def add_authors():
    authors = Author.query.all()
    return render_template("author.html", authors = authors)

@app.route("/books/<id>")
def books(id):
    book_id = Book.query.get(id)
    additional_authors = Author.query.all()
    return render_template("book_author.html", book = book_id, authors = additional_authors)

@app.route("/authors/<id>")
def authors(id):
    author_id = Author.query.get(id)
    additional_books = Book.query.all()
    return render_template("author_book.html", author = author_id, books = additional_books)

@app.route("/add", methods=['POST'])
def add():
    if request.form['add'] == 'add_book':
        new_book = Book(title = request.form['title'], description = request.form['description'])
        db.session.add(new_book)
        db.session.commit()
        return redirect("/")
    elif request.form['add'] == 'add_author':
        new_author = Author(first_name = request.form['first_name'], last_name = request.form['last_name'], notes = request.form['notes'])
        db.session.add(new_author)
        db.session.commit()
        return redirect("/authors")
    elif request.form['add'] == 'authors_of_books':
        existing_book = Book.query.get(request.form['book_id'])
        existing_author = Author.query.get(request.form['author_of_book'])
        existing_book.book_authors.append(existing_author)
        db.session.commit()
        id = request.form['book_id']
        return redirect("/")
    elif request.form['add'] == 'books_by_authors':
        existing_author = Author.query.get(request.form['author_id'])
        existing_book = Book.query.get(request.form['book_by_author'])
        existing_author.author_of_books.append(existing_book)
        db.session.commit()
        id = request.form['author_id']
        return redirect("/authors")

if __name__ == "__main__":
    app.run(debug=True)
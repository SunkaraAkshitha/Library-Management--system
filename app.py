from flask import Flask,render_template,request,redirect,url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)
class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200))
    email=db.Column(db.String(200),unique=True)
class Book(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200))
    author=db.Column(db.String(200))
    available=db.Column(db.Boolean,default=True)
class Borrow(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey("student.id"))
    book_id=db.Column(db.Integer,db.ForeignKey("book.id"))
    borrow_date=db.Column(db.DateTime,default=datetime.utcnow)
@app.route("/add_student",methods=["GET",'POST'])
def add_student():
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        student=Student(name=name,email=email)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("students"))
    return render_template("add_student.html")
@app.route("/students")
def students():
    all_students=Student.query.all()
    return render_template("students.html",students=all_students)
@app.route("/add_book",methods=["GET",'POST'])
def add_book():
    if request.method=="POST":
        title=request.form["title"]
        author=request.form["author"]
        book=Book(title=title,author=author)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for("books"))
    return render_template("add_book.html")
@app.route("/books")
def books():
    all_books=Book.query.all()
    return render_template("books.html",books=all_books)
@app.route("/borrow",methods=["GET","POST"])
def borrow():
    students=Student.query.all()
    books=Book.query.all()
    if request.method=="POST":
        student_id=request.form["student"]
        book_id=request.form["book"]
        book=Book.query.get(book_id)
        if not book.available:
            return "Book is already available"
        borrow=Borrow(student_id=student_id,book_id=book_id)
        db.session.add(borrow)
        db.session.commit()
        return redirect(url_for("borrowed"))
    return render_template("borrow.html",students=students,books=books)
@app.route("/borrowed")
def borrowed():
    data=db.session.query(
        Borrow.id,
        Student.name,
        Book.title,
        Borrow.borrow_date
    ).join(Student,Student.id==Borrow.student_id
    ).join(Book,Book.id==Borrow.book_id).all()
    return render_template("borrowed.html",data=data)
@app.route("/return/<int:id>")
def return_book(id):
    record=Borrow.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for("borrowed"))
@app.route("/search_book",methods=["GET","POST"])
def search_book():
    books=[]
    if request.method=="POST":
        keyword=request.form["keyword"]
        books=Book.query.filter(Book.title.contains(keyword)).all()
    return render_template("search_book.html",books=books)
@app.route("/")
def home():
    total_student=Student.query.count()
    total_book=Book.query.count()
    total_borrow=Borrow.query.count()
    return render_template("home.html",student=total_student,book=total_book,borrow=total_borrow)
if __name__=="__main__":
    app.run(debug=True)
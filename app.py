from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
from search import FlightSearch

app = Flask(__name__)
app.config["SECRET_kEY"] = os.urandom(16)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(16)
db = SQLAlchemy(app)


class Flights(db.Model):
    __tablename__ = "flight"
    id = db.Column(db.Integer, primary_key=True)
    # Relationship to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="flight")

    price = db.Column(db.Integer, nullable=True)
    origin_city = db.Column(db.String(50), nullable=True)
    origin_airport = db.Column(db.String(50), nullable=True)
    destination_city = db.Column(db.String(50), nullable=True)
    destination_airport = db.Column(db.String(50), nullable=True)
    out_date = db.Column(db.String(50), nullable=True)
    return_date = db.Column(db.String(50), nullable=True)
    stop_overs = db.Column(db.String(50), nullable=True)
    via_city = db.Column(db.String(50), nullable=True)
    link = db.Column(db.String(250), nullable=True)

    def to_dictionary(self):
        return {flight.name: getattr(self, flight.name) for flight in self.__table__.columns}

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    p = db.Column(db.String(100), nullable=False)
    flight = relationship("Flights", back_populates="user")


with app.app_context():
    # db.session.add(new_user)
    # db.session.commit()
    db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        user = db.session.query(User).filter_by(email=email).first()
        print(user, email)
        if not user:
            flash("查無此人")
            return redirect(url_for("index"))
        else:
            print(request.form.get("email"))
            login_user(user)
            return redirect(url_for("search_flights"))

    return render_template("login.html")




@app.route("/search", methods=["POST", "GET"])
@login_required
def search_flights():
    if request.method == "POST":
        code = request.form.get("code")
        flight_search = FlightSearch()
        data = flight_search.search_flight(code)
        new_flight = Flights(
            price=data["price"],
            origin_city=data["cityFrom"],
            origin_airport=data["cityCodeFrom"],
            destination_city=data["cityTo"],
            destination_airport=data["cityCodeTo"],
            out_date=f"{data['utc_departure'][:10]} {data['utc_departure'][11:19]}",
            return_date=f"{data['route'][-1]['utc_arrival'][:10]} {data['route'][-1]['utc_arrival'][11:19]}",
            stop_overs="null",
            via_city=data["route"][0]["cityTo"],
            link=data["deep_link"]
        )
        db.session.add(new_flight)
        db.session.commit()
        data = jsonify(flight=new_flight.to_dictionary())
        # Return json
        # return data
        return render_template("flight_search.html", flight=data)
    return render_template("flight_search.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

with app.app_context():
    db.create_all()


@app.route("/")
def get_all_cafes():
    query = db.select(Cafe)

    # Apply filters if provided
    location = request.args.get("location")
    has_wifi = request.args.get("wifi")
    has_toilet = request.args.get("toilet")
    has_sockets = request.args.get("sockets")
    can_take_calls = request.args.get("calls")
    max_price = request.args.get("price")

    if location:
        query = query.where(Cafe.location.ilike(f"%{location}%"))
    if has_wifi == "1":
        query = query.where(Cafe.has_wifi.is_(True))
    if has_toilet == "1":
        query = query.where(Cafe.has_toilet.is_(True))
    if has_sockets == "1":
        query = query.where(Cafe.has_sockets.is_(True))
    if can_take_calls == "1":
        query = query.where(Cafe.can_take_calls.is_(True))
    if max_price:
        query = query.where(Cafe.coffee_price <= max_price)

    result = db.session.execute(query.order_by(Cafe.name))
    cafes = [cafe.to_dict() for cafe in result.scalars().all()]
    return render_template("index.html", cafes=cafes)


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name = request.form["name"],
            map_url = request.form["map_url"],
            img_url = request.form["img_url"],
            location = request.form["location"],
            seats = request.form["seats"],
            has_toilet = bool(request.form.get("has_toilet")),
            has_wifi = bool(request.form.get("has_wifi")),
            has_sockets = bool(request.form.get("has_sockets")),
            can_take_calls = bool(request.form.get("can_take_calls")),
            coffee_price = request.form["coffee_price"]
        )
        try:
            db.session.add(new_cafe)
            db.session.commit()
            return redirect(url_for("get_all_cafes"))
        except Exception as e:
            flash("Error adding cafe. Make sure the name is unique.")
            db.session.rollback()
    return render_template("add_cafe.html")


@app.route("/delete/<int:cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    try:
        db.session.delete(cafe)
        db.session.commit()
        flash(f"Deleted cafe: {cafe.name}", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting cafe.", "danger")
    return redirect(url_for("get_all_cafes"))


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request
import requests

posts = requests.get("https://api.npoint.io/232e39b69bdbbbde009e").json()

app = Flask(__name__)


@app.route('/')
def get_all_posts():
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form.get("phone", "")
            message = request.form["message"]

            print(f"New message:\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}")

            return render_template("contact.html", success=True)
        except Exception as e:
            print("Error processing contact form:", e)
            return render_template("contact.html", error=True)

    return render_template("contact.html")


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


if __name__ == "__main__":
    app.run(port=5001)

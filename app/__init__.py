import os
import datetime
from flask import Flask, render_template, request
from dotenv import load_dotenv
from peewee import *
from playhouse.shortcuts import model_to_dict

load_dotenv()

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase(
        'file:memory?mode=memory&cache=shared',
        uri=True
    )
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE") or os.getenv("MYSQL_DB") or "myportfoliodb",
        user=os.getenv("MYSQL_USER") or "myportfolio",
        password=os.getenv("MYSQL_PASSWORD") or "mypassword",
        host=os.getenv("MYSQL_HOST") or "mysql",
        port=3306
    )

print(mydb)

class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb

mydb.connect()
mydb.create_tables([TimelinePost])

app = Flask(__name__)

# Data structure to feed Jinja templates dynamically
portfolio_data = {
    "profile": {
        "name": "Krishay Garg",
        "headline": "Production Engineering Fellow, Meta x MLH | Software Developer",
        "about_me": (
            "My name is Krishay and I am a computer science student at UCLA. "
            "I enjoy working on projects involving software engineering and machine learning, "
            "and I'm excited to expand my skills in production engineering. Some of my recent projects "
            "are translating videos to other languages with lipsync and training an LLM to play chess. "
            "In the past, I've also interned with a stealth startup working in the healthtech field."
        ),
        "profile_pic": "./static/img/profile_picture.png"
    },
    "work_experiences": [
        {
            "company": "Stealth AI Startup",
            "role": "Software Engineering Intern",
            "dates": "Nov 2025 - Present",
            "bullets": [
                "Architected AI pipelines in Python, integrating LangChain RAG, AI agents, and transformer based sentiment analysis models to evaluate bias in 523K+ research papers; automated cloud deployments using Render and AWS cron jobs.",
                "Engineered data pipelines via Selenium web scraping, utilizing MongoDB (NoSQL) for unstructured document storage, integrating Supabase (PostgreSQL) for vector embeddings, and applying Redis caching to optimize query retrieval."
            ]
        },
        {
            "company": "League of Women Voters",
            "role": "Software Engineering Intern",
            "dates": "Aug 2022 - Sept 2025",
            "bullets": [
                "Built VerifyIt, a multiplayer civics education web app with real-time WebSockets synchronization using React, Node.js, Flask, and PostgreSQL.",
                "Scaled to 100,000+ active users and featured on NPR (Here & Now).",
                "Automated campaign finance audit reporting using Pandas, NumPy, and Matplotlib data-processing pipelines, saving hundreds of staff hours."
            ]
        },
        {
            "company": "StemChef",
            "role": "Software Engineering Intern",
            "dates": "Mar 2024 - June 2025",
            "bullets": [
                "Led development of immersive augmented reality (AR) educational applications using Unity, C#, and TypeScript."
            ]
        }
    ],
    "education": [
        {
            "school": "University of California, Los Angeles (UCLA)",
            "degree": "BS Computer Science",
            "dates": "Graduating June 2028",
            "highlights": "GPA: 4.0"
        }
    ],
    "hobbies": [
        {
            "name": "Quiz Bowl",
            "description": "Active competitor in Quiz Bowl, recently placing 2nd at the college national championships.",
            "image": "./static/img/quiz_bowl.png"
        },
        {
            "name": "Board Games",
            "description": "Enjoy playing tactical board games (like Chess, Settlers of Catan, and strategy games) with friends.",
            "image": "./static/img/board_games.png"
        }
    ],
    "locations": [
        {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "desc": "Studying CS at UCLA!"},
        {"name": "San Diego", "lat": 32.7157, "lon": -117.1611, "desc": "Visited beautiful beaches and coastal areas."},
        {"name": "SF Bay Area", "lat": 37.7749, "lon": -122.4194, "desc": "Exploring the tech hub during breaks."},
        {"name": "Barcelona, Spain", "lat": 41.3851, "lon": 2.1734, "desc": "Explored Gaudi's architecture and historic streets."},
        {"name": "India", "lat": 28.6139, "lon": 77.2090, "desc": "Visiting family and exploring rich heritage."}
    ]
}


@app.route('/')
def index():
    return render_template(
        'index.html',
        title="MLH Fellow",
        url=os.getenv("URL"),
        active_page="home",
        **portfolio_data
    )


@app.route('/hobbies')
def hobbies():
    return render_template(
        'hobbies.html',
        title="Krishay Garg | Hobbies",
        url=os.getenv("URL"),
        active_page="hobbies",
        **portfolio_data
    )


@app.route('/timeline')
def timeline():
    return render_template(
        'timeline.html',
        title="Krishay Garg | Timeline",
        url=os.getenv("URL"),
        active_page="timeline",
        **portfolio_data
    )


@app.route('/api/timeline_post', methods=['POST'])
def post_time_line_post():
    name = request.form.get('name')
    if not name or name.strip() == "":
        return "Invalid name", 400

    email = request.form.get('email')
    import re
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email or not re.match(email_regex, email):
        return "Invalid email", 400

    content = request.form.get('content')
    if not content or content.strip() == "":
        return "Invalid content", 400

    timeline_post = TimelinePost.create(name=name, email=email, content=content)
    return model_to_dict(timeline_post)


@app.route('/api/timeline_post', methods=['GET'])
def get_time_line_post():
    return {
        'timeline_posts': [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }


@app.route('/api/timeline_post', methods=['DELETE'])
def delete_time_line_post():
    id = request.form.get('id') or request.args.get('id')
    if not id:
        return {"error": "Missing ID"}, 400
    try:
        post = TimelinePost.get_by_id(id)
        post.delete_instance()
        return {"message": f"Successfully deleted post {id}"}
    except TimelinePost.DoesNotExist:
        return {"error": "Post not found"}, 404

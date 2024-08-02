from flask import Flask, render_template, request, logging
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gpa_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class GPARecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(100), nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    message = db.Column(db.String(200), nullable=False)

    def __init__(self, name, department, level, gpa, message):
        self.name = name
        self.department = department
        self.level = level
        self.gpa = gpa
        self.message = message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        name = request.form['name']
        department = request.form['department']
        level = request.form['level']
        courses = int(request.form['courses'])  # Convert to integer

        total_units = 0
        total_points = 0

        for i in range(1, courses + 1):
            course_code = request.form[f'course{i}_code']
            score = int(request.form[f'course{i}_score'])
            units = int(request.form[f'course{i}_units'])

            if score >= 70:
                grade = 5
            elif score >= 60:
                grade = 4
            elif score >= 50:
                grade = 3
            elif score >= 45:
                grade = 2
            elif score >= 40:
                grade = 1
            else:
                grade = 0

            total_units += units
            total_points += grade * units

        gpa = round(total_points / total_units, 2) if total_units else 0.0

        # Determine the appropriate message
        if 4.5 <= gpa <= 5.0:
            message = f"Dear Scholar {name}, you are on first class."
        elif 3.5 <= gpa < 4.5:
            message = f"You are on second class upper, it is possible to make a first class. Continue pushing, {name}."
        elif 2.5 <= gpa < 3.5:
            message = f"You are on second class lower. There is enough space in Second class upper, get in there, {name}!"
        elif 1.5 <= gpa < 2.5:
            message = f"You are on third class! This isn't your best {name}, do more next semester."
        else:
            message = "You are on Pass! This is unlike you."

        # Save the record to the database
        new_record = GPARecord(name, department, level, gpa, message)
        db.session.add(new_record)
        db.session.commit()

        return render_template('result.html', name=name, gpa=gpa, message=message)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return "An error occurred while processing your request.", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

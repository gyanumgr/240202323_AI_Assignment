from flask import Flask, render_template, request
import rdflib
import math

app = Flask(__name__)

# Load the ontology
g = rdflib.Graph()
g.parse('mathonto.owl', format='application/rdf+xml')

nif = rdflib.Namespace('http://example.org/MathITS#')
ex = rdflib.Namespace('http://example.org/MathITS#')
g.bind('nif', nif)
g.bind('ex', ex)

# Function to fetch shape formulas from the ontology
# Function to fetch shape formulas from the ontology
# def get_shape_formulas():
#     query = """
#     PREFIX ex: <http://example.org/MathITS#>
#     SELECT ?shape ?formula
#     WHERE {
#         ?shape ex:hasExample ?formula_uri .
#         ?formula_uri ex:hasFormula ?formula .
#     }
#     """
#     result = g.query(query)
#     shape_formulas = {}
#     for row in result:
#         shape_name = row.shape.split("#")[-1].lower()  # Extract shape name
#         shape_formulas[shape_name] = str(row.formula)  # Store formula in dictionary
#     return shape_formulas

# from flask import Flask, render_template, request
# import rdflib
# import math

# app = Flask(__name__)

# # Load the ontology
# g = rdflib.Graph()
# g.parse('newowlfile.owl', format='application/rdf+xml')
# nif = rdflib.Namespace('http://example.org/MathITS#')
# g.bind('nif', nif)

# Function to fetch shape formulas from the ontology
def get_shape_formulas():
    query = """
    PREFIX nif: <http://example.org/MathITS#>
    SELECT ?shape ?formula
    WHERE {
        ?shape nif:hasExample ?formula_uri . 
        ?formula_uri nif:hasFormula ?formula . 
    }
    """
    result = g.query(query)
    shape_formulas = {}
    for row in result:
        shape_name = row.shape.split("#")[-1].lower()  # Extract shape name
        shape_formulas[shape_name] = row.formula  # Store formula in dictionary
    return shape_formulas


# Fetch formulas
shape_formulas = get_shape_formulas()


# Function to calculate the area of a shape
def calculate_area(shape, **params):
    shape = shape.lower()
    if shape not in shape_formulas:
        raise ValueError(f"Shape '{shape}' is not defined in the ontology.")
    
    formula = shape_formulas[shape]
    
    
    # Replace π with math.pi for evaluation
    formula = formula.replace("π", "math.pi")
    
    try:
        # Evaluating the formula dynamically
        return eval(formula, {"math": math}, params)
        
    except Exception as e:
        raise ValueError(f"Error in calculating area for shape '{shape}': {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    shape = None
    params = {}

    if request.method == "POST":
        shape = request.form["shape"].lower()
        if shape == "triangle":
            params["base"] = float(request.form["base"])
            params["height"] = float(request.form["height"])
        elif shape == "square":
            params["side"] = float(request.form["side"])
        elif shape == "rectangle":
            params["length"] = float(request.form["length"])
            params["width"] = float(request.form["width"])
        elif shape == "circle":
            params["radius"] = float(request.form["radius"])

        try:
            result = calculate_area(shape, **params)
            print(f"The area is: ", {result})
        except ValueError as e:
            error = str(e)

    return render_template("maths.html", result=result, error=error, shape=shape)

# Function to fetch quiz questions from the ontology
query = """
PREFIX nif: <http://www.w3.org/2005/11/nif#>
PREFIX ex: <http://example.org/MathITS#>

SELECT ?question ?text ?option1 ?option2 ?option3 ?option4 ?correct_answer
WHERE {
    ?question a ex:MultipleChoiceQuestion ;
              ex:hasQuestionText ?text ;
              ex:hasOption1 ?option1 ;
              ex:hasOption2 ?option2 ;
              ex:hasOption3 ?option3 ;
              ex:hasOption4 ?option4 ;
              ex:hasCorrectAnswer ?correct_answer .
}
"""

# Function to execute the SPARQL query and return the results as a list of dictionaries
def get_quiz_questions():
    results = g.query(query)
    quiz_questions = []
    
    for row in results:
        question = {
            "text": str(row.text),
            "options": {
                "option1": str(row.option1),
                "option2": str(row.option2),
                "option3": str(row.option3),
                "option4": str(row.option4),
            },
            "correct_answer": str(row.correct_answer),
        }
        quiz_questions.append(question)
    
    return quiz_questions

@app.route('/quiz')
def home():
    quiz_questions = get_quiz_questions()  # Get the quiz questions using SPARQL
    return render_template('quizzes.html', quiz_questions=quiz_questions)

@app.route('/submit', methods=['POST'])
def submit_quiz():
    quiz_questions = get_quiz_questions()
    score = 0
    results = []
    
    # Check answers
    for idx, question in enumerate(quiz_questions):
        selected_answer = request.form.get(f'question{idx+1}')
        correct_answer = question['correct_answer']
        
        # Check if the selected answer matches the correct one
        if selected_answer == correct_answer:
            score += 1
            result = 'Correct'
        else:
            result = 'Incorrect'
        
        results.append({
            'question': question['text'],
            'selected_answer': selected_answer,
            'correct_answer': correct_answer,
            'result': result
        })
    
    return render_template('results.html', score=score, total=len(quiz_questions), results=results)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
db = SQLAlchemy(server)
#Creating server

ingredient_num = 1

filters = [
    {
        'filter': 'dairy',
        'id':'D-'
    },
    {
        'filter': 'gluten',
        'id':'G-'
    },
    {
        'filter': 'treenut',
        'id':'NT'
    },
    {
        'filter': 'peanut',
        'id':'NP'
    },
    {
        'filter': 'coconut',
        'id':'NC'
    },
    {
        'filter': 'shellfish',
        'id':'SS'
    },
    {
        'filter': 'soy',
        'id':'Y-'
    },
    {
        'filter': 'fish',
        'id':'SF'
    },
    {
        'filter': 'egg',
        'id':'E-'
    }
]
#Establishing dictionary of Tags/Filters

class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, default="None Listed")
    chef = db.Column(db.Text, nullable=False, default="None Listed")
    ingredients = db.Column(db.Text, nullable=False, default="None Listed")
    steps = db.Column(db.Text, nullable=False, default="None Listed")
    extra_notes = db.Column(db.Text, nullable=False, default="")
    tags = db.Column(db.Text, nullable=False, default="")
    
    def __repr__(self):
        return 'New Recipe: ' + str(self.id) 
#Configuring Database Database

@server.route('/')
def index():
    return render_template('index.html')
#Routing to Home Page

@server.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'POST':
        #if new recipe input

        ingredient_num = 1
        recipe_name = request.form['name']
        recipe_chef = request.form['chef']
        recipe_ingredients = request.form['ingredients']
        recipe_steps = request.form['steps']
        recipe_extra_notes = request.form['notes']
        recipe_tags = ""
        #assigning new recipe ject to form inputs

        for my_filter in filters:
            try:
                if request.form[my_filter['filter']] == "":
                    recipe_tags += my_filter['id']
            except:
                continue
        #assigning tags to recipe
        
        new_recipes = Recipes(name=recipe_name, chef=recipe_chef, ingredients=recipe_ingredients, steps=recipe_steps, extra_notes=recipe_extra_notes, tags=recipe_tags)
        db.session.add(new_recipes)
        db.session.commit()
        return redirect('/add')
        #adding recipe to database
        
    else:
        ingredient_num = 0
        return render_template("add.html", used_filters=filters, ing_num=ingredient_num)
        #displaying website


@server.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        #if search is input

        search = request.form['search']
        all_recipes = Recipes.query.all()
        correct_recipes = []
        tag_check = []

        for my_filter in filters:
            try:
                if request.form[my_filter['filter']] == "":
                    tag_check.append(my_filter['id'])
            except:
                continue
        #Identifying tags to exclude

        for recipe in all_recipes:   
            name = str(recipe.name)
            try:
                temp = name.index(search)
                #test if search exist
            except:
                continue
            else:
                i = 0
                print("Test1")
                for tag in tag_check:
                    i = 0
                    try:
                        temp = recipe.tags.index(tag)
                    except:
                        i = i**2
                    else:
                        i = i + 1
                        break
                #checking if excluded tags are included
                if i == 0:
                    correct_recipes.append(recipe)
                #adds to results





                    
        if correct_recipes != []:
            #if recipes then show results
            return render_template("results.html", recipes=correct_recipes, used_filters=filters)
        else:
            #if none say failed
            return render_template("search.html", search=0, failure=1, used_filters=filters)

    else:
        #if search is input
        return render_template("search.html", search=0, failure=0, used_filters=filters)

@server.route('/recipe', methods=['GET', 'POST'])
def recipe():

    if request.method == 'POST':
        #if new recipe input

        recipe_name = request.form['name']
        recipe_chef = request.form['chef']
        recipe_ingredients = request.form['ingredients']
        recipe_steps = request.form['steps']
        recipe_extra_notes = request.form['notes']
        recipe_tags = ""
        #assigning new recipe ject to form inputs

        for my_filter in filters:
            try:
                if request.form[my_filter['filter']] == "":
                    recipe_tags += my_filter['id']
            except:
                continue
        #assigning tags to recipe
        
        new_recipes = Recipes(name=recipe_name, chef=recipe_chef, ingredients=recipe_ingredients, steps=recipe_steps, extra_notes=recipe_extra_notes, tags=recipe_tags)
        db.session.add(new_recipes)
        db.session.commit()
        return redirect('/recipe')
        #adding recipe to database
        
    else:
        all_recipes = Recipes.query.order_by(Recipes.name).all()
        return render_template("recipe.html", recipes=all_recipes, used_filters=filters)
        #displaying website

@server.route('/recipe/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    recipe = Recipes.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect('/recipe')
    #deleting recipe from database

if __name__ == "__main__":
    server.run(debug=True)
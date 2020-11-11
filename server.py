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
#Configuring Recipe Database Database



class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, default="None Listed")
    password = db.Column(db.Text, nullable=False, default="Password")
    favorites = db.Column(db.Text, nullable=False, default="")
    group_ids = db.Column(db.Text, nullable=False, default="")

    
    def __repr__(self):
        return 'New User: ' + str(self.id)



class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.Text, nullable=False, default="No Name")
    recipe_ids = db.Column(db.Text, nullable=False, default="")
    
    def __repr__(self):
        return 'New Group: ' + str(self.id) 



@server.route('/')
def index():
    return render_template('index.html')
#Routing to Home Page



@server.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        loginUsername = request.form['username']
        loginPassword = request.form['password']
        users = Users.query.all()
        for user in users:
            if user.username == loginUsername and user.password == loginPassword:
                currentUser = user
                return render_template('userpage.html', theUser=user)
        return render_template('login.html', failure = 1)

    else:
        return render_template('login.html')



@server.route('/newuser', methods=['GET', 'POST'])
def newuser():
    
    if request.method == 'POST':

        newUsername = request.form['username']
        newPassword = request.form['password']
        users = Users.query.all()
        
        for user in users:
            if user.username == newUsername and user.password == newPassword:
                return render_template('userpage.html', theUser=user, weirdness=1)

        newUser = Users(username=newUsername, password=newPassword)
        db.session.add(newUser)
        db.session.commit()
        return render_template('userpage.html', theUser=newUser, new=1)

    else:
        return render_template('newuser.html')



@server.route('/manager', methods=['GET', 'POST'])
def manager():

    if request.method == 'POST':

        new_group = Groups(group_name=request.form['manager'])
        db.session.add(new_group)
        db.session.commit()

        return redirect('/manager')

    else:

        try:
            if currentUser.username != '':
                myGroups = []
                userGroups = []
                recipes = Recipes.query.all()
                for n in range(0, len(currentUser.group_ids)):
                        if currentUser.group_ids[n:n+1] == "|":
                            for group in Groups.query.all():
                                try:
                                    tempm = int(tempn)
                                except:
                                    continue
                                if group.id == int(tempm):
                                    userGroups.append(group)
                                    tempn = ""
                        else:
                            tempn = tempn + str(currentUser.group_ids[n:n+1])
                for group in userGroups:
                    thisNewGroup = []
                    tempv = ""
                    thisNewGroup.append(group)
                    for v in range(0, len(group.recipe_ids)):
                        if group.recipe_ids[v:v+1] == "|":
                            for recipe in recipes:
                                try:
                                    templ = int(tempv)
                                except:
                                    continue
                                if recipe.id == int(templ):
                                    thisNewGroup.append(recipe)
                                    tempv = ""
                        else:
                            tempv = tempv + str(group.recipe_ids[v:v+1])
                    if len(thisNewGroup) == 0:
                        thisNewGroup.append("None Listed")
                    myGroups.append(thisNewGroup)

        except:
            myGroups = []
            recipes = Recipes.query.all()
            for group in Groups.query.all():
                thisNewGroup = []
                tempv = ""
                thisNewGroup.append(group)
                for v in range(0, len(group.recipe_ids)):
                    if group.recipe_ids[v:v+1] == "|":
                        for recipe in recipes:
                            try:
                                templ = int(tempv)
                            except:
                                continue
                            if recipe.id == int(templ):
                                thisNewGroup.append(recipe)
                                tempv = ""
                    else:
                        tempv = tempv + str(group.recipe_ids[v:v+1])
                if len(thisNewGroup) == 0:
                    thisNewGroup.append("None Listed")
                myGroups.append(thisNewGroup)

        return render_template('manager.html', the_groups = myGroups, used_filters=filters)



@server.route('/manager/addToGroup/<int:gid>/<int:id>', methods=['GET', 'POST'])
def addToGroup(gid, id):
    group = Groups.query.get_or_404(gid)
    tempz = group.recipe_ids
    if len(tempz) == 0:
        tempz = "|"
    tempz = tempz + str(id) + "|"
    group.recipe_ids = tempz
    db.session.commit()
    return redirect('/recipe')

@server.route('/manager/deleteGroup/<int:id>')
def deleteGroup(id):
    group = Groups.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    return redirect('/manager')
    #deleting recipe from database

@server.route('/manager/deleteFromGroup/<int:gid>/<int:id>')
def deleteFromGroup(gid, id):
    group = Groups.query.get_or_404(gid)
    if group.recipe_ids.index("|" + str(id)) != 0:
        group.recipe_ids = group.recipe_ids[0:group.recipe_ids.index("|" + str(id) + "|")] + group.recipe_ids[group.recipe_ids.index("|" + str(id) + "|") + len(str(id)) + 1:len(group.recipe_ids)]
    else:
        group.recipe_ids = group.recipe_ids[len(str(id)) + 1:len(group.recipe_ids)]
    db.session.commit()

    return redirect('/manager')



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
            return render_template("results.html", the_groups = Groups.query.all(), recipes=correct_recipes, used_filters=filters)
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
        all_recipes = Recipes.query.all()
        inputGroups = Groups.query.all()
        return render_template("recipe.html", recipes=all_recipes, used_filters=filters, the_groups=inputGroups)
        #displaying website



@server.route('/recipe/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    recipe = Recipes.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect('/recipe')
    #deleting recipe from database



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

if __name__ == "__main__":
    server.run(debug=True)
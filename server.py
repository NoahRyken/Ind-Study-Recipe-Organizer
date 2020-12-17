from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
db = SQLAlchemy(server)
#Creating server

ingredient_num = 1
currentUser = -1

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
    return render_template('index.html', user=currentUser)
#Routing to Home Page



@server.route('/reset')
def reset():

    recipes = Recipes.query.all()
    groups = Groups.query.all()
    users = Users.query.all()

    for recipe in recipes:
        db.session.delete(recipe)
    for group in groups:
        db.session.delete(group)
    for user in users:
        db.session.delete(user)

    db.session.commit()

    return redirect('/')



@server.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('logout.html')



@server.route('/logout/confirm', methods=['GET', 'POST'])
def logoutConfirmed():

    global currentUser
    currentUser = -1

    return redirect('/')



@server.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        
        global currentUser
        loginUsername = request.form['username']
        loginPassword = request.form['password']
        users = Users.query.all()

        for user in users:
            if user.username == loginUsername and user.password == loginPassword:
                currentUser = user.id
                return redirect('/manager')

        return render_template('login.html', failure = 1)

    else:
        return render_template('login.html')



@server.route('/newuser', methods=['GET', 'POST'])
def newuser():
    
    if request.method == 'POST':
        
        global currentUser
        newUsername = request.form['username']
        newPassword = request.form['password']
        users = Users.query.all()
        
        for user in users:
            if user.username == newUsername and user.password == newPassword:
                return render_template('userpage.html', theUser=user, weirdness=1)
            elif user.username == newUsername:
                return render_template('newuser.html', inUse=1)

        newUser = Users(username=newUsername, password=newPassword)
        db.session.add(newUser)
        db.session.commit()
        currentUser = newUser.id
        return render_template('userpage.html', theUser=newUser, new=1)

    else:
        return render_template('newuser.html')



@server.route('/userGroupManager/<int:id>')
def addGroupUser(id):

    user = Users.query.get_or_404(currentUser)
    group = Groups.query.get_or_404(id)

    groupIds = user.group_ids

    if groupIds == "":
        groupIds = "|" + str(group.id) + "|"
    else:
        groupIds = groupIds + str(group.id) + "|"

    user.group_ids = groupIds
    db.session.commit()
    
    return redirect('/userGroupManager')



@server.route('/userGroupDelete/<int:id>')
def userGroupDelete(id):

    user = Users.query.get_or_404(currentUser)
    userGroups = user.group_ids

    if userGroups.index("|" + str(id)) != 0:
        userGroups = userGroups[0:userGroups.index("|" + str(id))] + userGroups[userGroups.index("|" + str(id)) + len(str(id)) + 1:len(userGroups)]
    
    else:
        userGroups = userGroups[len(str(id)) + 1:len(userGroups)]

    user.group_ids = userGroups
    db.session.commit()
    return redirect('/userGroupManager')



@server.route('/userGroupManager')
def userGroupManager():

    user = Users.query.get_or_404(currentUser)
    groups = Groups.query.all()
    recipes = Recipes.query.all()
    usedGroupList = []
    usedRecipes = []

    for group in groups:
        try:
            if user.group_ids.index("|" + str(group.id) + "|") != -1:
                usedGroupList.append(group)
        except:
            continue

    for group in usedGroupList:
        groupsRecipes = []
        groupsRecipes.append(group)
        for recipe in recipes:
            try:
                if group.recipe_ids.index("|" + str(recipe.id) + "|" != -1):
                    groupsRecipes.append(recipe)
            except:
                continue
        usedRecipes.append(groupsRecipes)
            
    return render_template('usergroupmanager.html', usedGroups=usedRecipes, currentUser=user, theGroups=groups)



@server.route('/manager', methods=['GET', 'POST'])
def manager():

    if request.method == 'POST':

        new_group = Groups(group_name=request.form['manager'])
        db.session.add(new_group)
        db.session.commit()

        return redirect('/manager')

    else:

        if currentUser != -1:
            theUser = Users.query.get_or_404(currentUser)
            myGroups = []
            tempn = ""
            userGroups = []
            recipes = Recipes.query.all()
            for n in range(1, len(theUser.group_ids)):
                if theUser.group_ids[n:n+1] != "|":
                    tempn = tempn + str(theUser.group_ids[n:n+1])
                else:
                    id = int(tempn)
                    tempn = ""
                    for group in Groups.query.all():
                        if id == group.id:
                            userGroups.append(group)
                            continue

            AllGroupIngredientsList = []
            AllGroupIngredientsAmount = []
            AllGroupIngredientsMessure = []
            groupNames = []

            for group in userGroups:

                GroupIngredientsList = []
                GroupIngredientsAmount = []
                GroupIngredientsMessure = []
                ingredientsAmount = []
                ingredientsMessure = []
                ingredientsList = []

                groupNames.append(group.group_name)

                thisNewGroup = []
                tempv = ""
                thisNewGroup.append(group)
                for v in range(0, len(group.recipe_ids)):
                    if group.recipe_ids[v:v+1] == "|":
                        for recipe in recipes:
                            try:
                                templ = int(tempv)
                                i = 0
                                for recipe in recipes:
                                    if recipe.id == templ:
                                        i = 1
                                        break
                                if i == 0:
                                    tempv = ""
                            except:
                                continue
                            if recipe.id == int(templ):
                                thisNewGroup.append(recipe)
                                tempv = ""

                                ingredientsRecipe = recipe.ingredients
                                temph = ""
                                for z in range(0, len(ingredientsRecipe)):
                                    tempChar = ingredientsRecipe[z:z+1]
                                    if z == 0:
                                        continue
                                    elif tempChar == "|":
                                        ingredientsList.append(temph)
                                        temph = ""
                                    elif tempChar == "*":
                                        ingredientsAmount.append(float(temph))
                                        temph = ""
                                    elif tempChar == ":":
                                        ingredientsMessure.append(temph)
                                        temph = ""
                                    else:
                                        temph = temph + tempChar
                    else:
                        tempv = tempv + str(group.recipe_ids[v:v+1])
                if len(thisNewGroup) == 0:
                    thisNewGroup.append("None Listed")
                myGroups.append(thisNewGroup)

                for a in range(0, len(ingredientsList)):
                    k = 0
                    for b in range(0, len(GroupIngredientsList)):
                        if ingredientsList[a] == GroupIngredientsList[b] and ingredientsMessure[a] == GroupIngredientsMessure[b]:
                            GroupIngredientsAmount[b] = GroupIngredientsAmount[b] + ingredientsAmount[a]
                            k = 1
                    if k != 1:
                        GroupIngredientsAmount.append(ingredientsAmount[a])
                        GroupIngredientsMessure.append(ingredientsMessure[a])
                        GroupIngredientsList.append(ingredientsList[a])
                        


                            
                AllGroupIngredientsAmount.append(GroupIngredientsAmount)
                AllGroupIngredientsMessure.append(GroupIngredientsMessure)
                AllGroupIngredientsList.append(GroupIngredientsList)
                

        else:
            theUser = "Guest"
            myGroups = []
            recipes = Recipes.query.all()

            AllGroupIngredientsList = []
            AllGroupIngredientsAmount = []
            AllGroupIngredientsMessure = []
            groupNames = []

            for group in Groups.query.all():

                GroupIngredientsList = []
                GroupIngredientsAmount = []
                GroupIngredientsMessure = []
                ingredientsAmount = []
                ingredientsMessure = []
                ingredientsList = []

                groupNames.append(group.group_name)

                thisNewGroup = []
                tempv = ""
                thisNewGroup.append(group)
                for v in range(0, len(group.recipe_ids)):
                    if group.recipe_ids[v:v+1] == "|":
                        for recipe in recipes:
                            try:
                                templ = int(tempv)
                                i = 0
                                for recipe in recipes:
                                    if recipe.id == templ:
                                        i = 1
                                        break
                                if i == 0:
                                    tempv = ""
                            except:
                                continue
                            if recipe.id == int(templ):
                                thisNewGroup.append(recipe)
                                tempv = ""

                                ingredientsRecipe = recipe.ingredients
                                temph = ""
                                for z in range(0, len(ingredientsRecipe)):
                                    tempChar = ingredientsRecipe[z:z+1]
                                    if z == 0:
                                        continue
                                    elif tempChar == "|":
                                        ingredientsList.append(temph)
                                        temph = ""
                                    elif tempChar == "*":
                                        ingredientsAmount.append(float(temph))
                                        temph = ""
                                    elif tempChar == ":":
                                        ingredientsMessure.append(temph)
                                        temph = ""
                                    else:
                                        temph = temph + tempChar
                    else:
                        tempv = tempv + str(group.recipe_ids[v:v+1])
                if len(thisNewGroup) == 0:
                    thisNewGroup.append("None Listed")
                myGroups.append(thisNewGroup)

                for a in range(0, len(ingredientsList)):
                    k = 0
                    for b in range(0, len(GroupIngredientsList)):
                        if ingredientsList[a] == GroupIngredientsList[b] and ingredientsMessure[a] == GroupIngredientsMessure[b]:
                            GroupIngredientsAmount[b] = GroupIngredientsAmount[b] + ingredientsAmount[a]
                            k = 1
                    if k != 1:
                        GroupIngredientsAmount.append(ingredientsAmount[a])
                        GroupIngredientsMessure.append(ingredientsMessure[a])
                        GroupIngredientsList.append(ingredientsList[a])
                        


                            
                AllGroupIngredientsAmount.append(GroupIngredientsAmount)
                AllGroupIngredientsMessure.append(GroupIngredientsMessure)
                AllGroupIngredientsList.append(GroupIngredientsList)

        finalList = []
        templist = []
        bigTempList = []
        for l in range(0, len(AllGroupIngredientsAmount)):
            bigTempList.append(groupNames[l])
            for z in range(0, len(AllGroupIngredientsAmount[l])):
                templist.append(AllGroupIngredientsAmount[l][z])
                templist.append(AllGroupIngredientsMessure[l][z])
                templist.append(AllGroupIngredientsList[l][z])
                bigTempList.append(templist)
                templist = []
            finalList.append(bigTempList)
            bigTempList = []

        return render_template('manager.html', LF=finalList, user=theUser, the_groups = myGroups, used_filters=filters)



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
        group.recipe_ids = group.recipe_ids[0:group.recipe_ids.index("|" + str(id) + "|")] + group.recipe_ids[group.recipe_ids.index("|" + str(id) + "|") + len(str(id)) + 1]
    else:
        group.recipe_ids = group.recipe_ids[len(str(id)) + 1]
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

    return render_template("recipe.html", recipes=Recipes.query.all(), used_filters=filters, the_groups=Groups.query.all())
    #displaying website



@server.route('/recipe/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    recipe = Recipes.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect('/recipe')
    #deleting recipe from database



@server.route('/addIngredients', methods=['GET', 'POST'])
def addIngredients():

    if request.method == 'POST':

        tempg = -1

        for recipe in Recipes.query.all():
            if recipe.id > tempg:
                tempg = recipe.id
        
        ingredientAmount = request.form['ingredient_amount'].lower()
        ingredientMeasure = request.form['ingredient_measure'].lower()
        ingredientName = request.form['ingredient_name'].lower()

        recipe = Recipes.query.get_or_404(tempg)
        recipe.ingredients = recipe.ingredients + ingredientAmount + "*" + ingredientMeasure + ":" + ingredientName + "|"
        db.session.commit()
        return redirect('/addIngredients')

    else:
        return render_template('addingredient.html')





@server.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'POST':
        #if new recipe input

        recipe_name = request.form['name']
        recipe_chef = request.form['chef']
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
        
        new_recipes = Recipes(name=recipe_name, chef=recipe_chef, ingredients="|", steps=recipe_steps, extra_notes=recipe_extra_notes, tags=recipe_tags)
        db.session.add(new_recipes)
        db.session.commit()
        return redirect("/addIngredients")
        #adding recipe to database
        
    else:
        ingredient_num = 0
        return render_template("add.html", used_filters=filters, ing_num=ingredient_num)
        #displaying website

if __name__ == "__main__":
    server.run(debug=True)
---
title: Game Management - Adding Games to Your Collection
description: Learn how to create forms to add, edit, and manage games in your GameVault collection. Fun and easy!
---


# 🎮 Game Management

Now for the fun part! Let's add the ability to actually add, edit, and manage games in your collection. This is where GameVault really comes to life!

## What we're building 🎯

We want users to be able to:
- ✅ **Add new games** with a simple form
- ✅ **Edit existing games** when they want to update info
- ✅ **Delete games** they no longer want to track
- ✅ **View their collection** in a nice list

<Steps>

1. **Connect users to games** �

   First, we need to make sure each game belongs to a specific user. We'll add a user-game relationship using Framefox's entity creation command.

   Let's add a relationship between Game and User entities:

   ```bash title="Add user relationship to games"
   framefox create entity
   ```

   Here's what the real interactive process looks like:

   ```bash title="Interactive relationship creation"
   What is the name of the Entity ?(snake_case)
   Entity name: game
   The entity 'game' already exists. You are updating it !

   Do you want to add a new property to the entity ?(press enter to quit the terminal)
   Property name: user

   Property type [?] (str): relation

   Enter the name of the target entity (snake_case) : user

   Select the type of relation:
   1. OneToOne  - "One Game is linked to One User"
   2. OneToMany  - "One Game is linked to Many User"
   3. ManyToOne  - "Many Game are linked to One User"
   4. ManyToMany  - "Many Game are linked to Many User"

   Enter the number corresponding to the type of relation: 3

   Can the relation be nullable? (yes): yes

   Do you want to add an inverse relation? (yes): 

   Enter the name of the inverse property in the target entity  (games): 
   Relation 'ManyToOne' created between 'game' and 'user'.

   Do you want to add a new property to the entity ?(press enter to quit the terminal)
   Property name: 
   No property entered. Closing terminal.
   ```

   **Amazing!** Framefox just automatically:
   - Added a `user_id` foreign key field to the `Game` entity
   - Added a `user` relationship property to access the linked User
   - Added a `games` relationship property to the `User` entity (the inverse relation)
   - Created the proper SQLModel relationships with foreign keys
   - Set up the bidirectional relationship between User and Game

   The generated code looks like this:

   ```python title="src/entity/game.py (automatically generated)"
   # Framefox added these automatically:
   user_id: int | None = Field(
       foreign_key='user.id', ondelete='CASCADE', nullable=False
   )
   user: User | None = Relationship(back_populates='games')
   ```

   ```python title="src/entity/user.py (automatically generated)"
   # Framefox added this automatically:
   games: list['Game'] = Relationship(back_populates='user')
   ```

   Now create and apply the migration:

   ```bash title="Apply the database changes"
   framefox database create-migration
   framefox database upgrade
   ```

   :::note[What did we just do?]
   We created a **ManyToOne** relationship where many games can belong to one user using [SQLModel relationships](/framefox/core/database). Framefox automatically generated all the necessary code - the foreign key field, the relationship properties, and even the inverse relationship. Now each user can have their own collection of games!
   :::

2. **Create the CRUD system** 📝

   Now let's create a complete CRUD (Create, Read, Update, Delete) system using the [interactive terminal](/framefox/advanced_features/terminal):

   ```bash title="Create CRUD system"
   framefox create crud
   ```

   Here's what the real interaction looks like:

   ```bash title="Interactive CRUD creation"
   What is the name of the entity you want to create a CRUD with ?(snake_case)
   Entity name: game

   What type of controller do you want to create?

   1. API CRUD controller
   2. Templated CRUD controller

   CRUD controller type (1-2) [1]: 2

   ✓ CRUD Controller created successfully: src/controller/game_controller.py
   ✓ Form type created successfully: src/form/game_type.py
   ✓ Template created successfully: templates/game/create.html
   ✓ Template created successfully: templates/game/read.html
   ✓ Template created successfully: templates/game/update.html
   ✓ Template created successfully: templates/game/index.html
   ```

   **Amazing!** Framefox just created:
   - A complete [controller](/framefox/core/controllers) with all CRUD operations
   - A form type for creating/editing games
   - HTML templates for all the pages
   - Everything wired up and ready to use!

   :::tip[What's CRUD?]
   CRUD stands for:
   - **C**reate - Add new games
   - **R**ead - View your games  
   - **U**pdate - Edit game info
   - **D**elete - Remove games

   It's the basic operations you need for any data management system using [forms and controllers](/framefox/core/forms)!
   :::

3. **Check out your new pages** 👀

   Now visit these URLs to see what Framefox created for you:

   - `http://localhost:8000/game` - List all your games
   - `http://localhost:8000/game/create` - Add a new game
   - `http://localhost:8000/game/1` - View a specific game (after you add one!)

   Try adding your first game! Fill out the form and hit submit. You should see it appear in your game list.

4. **Customize the form fields (Optional)** 🛠️

   The generated form works great, but let's make it even better for games! We can update the [form](/framefox/core/forms) to have proper dropdowns instead of text fields.

   Edit `src/form/game_type.py` and look for the platform field. Framefox created a basic text field, but let's make it a dropdown using [form field types](/framefox/core/forms):

   ```python title="src/form/game_type.py (find and update this part)"
   # You'll need to import ChoiceType at the top
   from framefox.core.form.field.choice_type import ChoiceType

   # Replace the platform field with this:
   builder.add("platform", ChoiceType, {
       "label": "Platform",
       "choices": [
           ("pc", "PC"),
           ("playstation", "PlayStation"),
           ("xbox", "Xbox"),
           ("nintendo", "Nintendo Switch"),
           ("mobile", "Mobile"),
       ],
       "attr": {"class": "form-select"}
   })

   # And update the status field:
   builder.add("status", ChoiceType, {
       "label": "Status",
       "choices": [
           ("playing", "Currently Playing"),
           ("completed", "Completed"),
           ("wishlist", "Wishlist"),
           ("backlog", "Backlog"),
           ("dropped", "Dropped"),
       ],
       "attr": {"class": "form-select"}
   })
   ```

   Now when you visit the add/edit game pages, you'll have nice dropdowns instead of text fields!

   :::note[Why update the form?]
   [Forms](/framefox/core/forms) are super important for user experience. Dropdowns prevent typos and make it easier for users to pick valid options. Much better than typing "nintendo swich" by mistake!
   :::
   })

   # And update the status field:
   builder.add("status", ChoiceType, {
       "label": "Status",
       "choices": [
           ("playing", "Currently Playing"),
           ("completed", "Completed"),
           ("wishlist", "Wishlist"),
           ("backlog", "Backlog"),
           ("dropped", "Dropped"),
       ],
       "attr": {"class": "form-select"}
   })
   ```

   Now when you visit the add/edit game pages, you'll have nice dropdowns instead of text fields!

   :::note[Why update the form?]
   [Forms](/framefox/core/forms) are super important for user experience. Dropdowns prevent typos and make it easier for users to pick valid options. Much better than typing "nintendo swich" by mistake!
   :::

4. **Make the list page awesome** 🌟

   The generated list page is functional, but let's make it look like a proper game collection. Edit `templates/game/index.html`:

   ```html title="templates/game/index.html"
   {% extends "base.html" %}

   {% block title %}My Game Collection{% endblock %}

   {% block body %}
   <div class="container mt-4">
       <div class="d-flex justify-content-between align-items-center mb-4">
           <h1>🎮 My Game Collection</h1>
           <a href="{{ url_for('game.create') }}" class="btn btn-primary">
               <i class="fas fa-plus"></i> Add New Game
           </a>
       </div>

       {% if games %}
       <div class="row">
           {% for game in games %}
           <div class="col-md-6 col-lg-4 mb-4">
               <div class="card h-100">
                   <div class="card-body">
                       <h5 class="card-title">{{ game.title }}</h5>
                       <p class="card-text">
                           <span class="badge bg-primary">{{ game.platform }}</span>
                           <span class="badge bg-secondary">{{ game.status }}</span>
                       </p>
                       {% if game.rating %}
                       <p class="card-text">
                           <small class="text-muted">Rating: {{ game.rating }}/10</small>
                       </p>
                       {% endif %}
                       {% if game.notes %}
                       <p class="card-text">{{ game.notes[:100] }}{% if game.notes|length > 100 %}...{% endif %}</p>
                       {% endif %}
                   </div>
                   <div class="card-footer">
                       <div class="btn-group w-100">
                           <a href="{{ url_for('game.show', id=game.id) }}" class="btn btn-outline-primary btn-sm">View</a>
                           <a href="{{ url_for('game.edit', id=game.id) }}" class="btn btn-outline-secondary btn-sm">Edit</a>
                           <form method="POST" action="{{ url_for('game.delete', id=game.id) }}" style="display: inline;" 
                                 onsubmit="return confirm('Are you sure you want to delete this game?')">
                               <button type="submit" class="btn btn-outline-danger btn-sm">Delete</button>
                           </form>
                       </div>
                   </div>
               </div>
           </div>
           {% endfor %}
       </div>
       {% else %}
       <div class="text-center mt-5">
           <i class="fas fa-gamepad fa-3x text-muted mb-3"></i>
           <h3>No games in your collection yet!</h3>
           <p class="text-muted">Start building your gaming library by adding your first game.</p>
           <a href="{{ url_for('game.create') }}" class="btn btn-primary btn-lg">
               <i class="fas fa-plus"></i> Add Your First Game
           </a>
       </div>
       {% endif %}
   </div>
   {% endblock %}
   ```

6. **Test everything!** 🧪

   Now let's try out all the features:

   1. **Add a game** - Go to `/game/create` and add a few games
   2. **View the list** - See them displayed nicely at `/game`
   3. **Edit a game** - Click "Edit" on any game card
   4. **Delete a game** - Click "Delete" (it will ask for confirmation)

   Pretty cool, right? You now have a fully functional game collection manager!

</Steps>

## What we accomplished 🏆

In this chapter, we added:

1. ✅ **User-game relationships** - Each game belongs to a specific user
2. ✅ **Complete CRUD operations** - Add, view, edit, delete games
3. ✅ **Professional forms** - With dropdowns and validation
4. ✅ **Beautiful game cards** - Visual list of your collection
5. ✅ **User-friendly interface** - Easy navigation and actions
6. ✅ **Safety features** - Confirmation before deleting

## Understanding the magic 🧙‍♂️

### Controllers
Handle the logic using [MVC architecture](/framefox/core/controllers) - what happens when someone submits a form or clicks a button.

### Forms  
Define what fields to show and how to validate user input using [Framefox forms](/framefox/core/forms).

### Templates
Control how everything looks in the browser using [Jinja2 templates](/framefox/core/templates).

### Repository
Handles saving/loading data from the database using the [repository pattern](/framefox/core/database) (Framefox does this automatically!).

:::tip[Don't worry about the code!]
You don't need to understand all the generated code yet. The important thing is that it works! As you get more comfortable, you can start customizing things.
:::

## Understanding the workflow 🔄

Here's what happens when you add a game:

1. **User visits** `/game/create`
2. **Controller shows** the form template
3. **User fills out** and submits form
4. **Controller validates** the data
5. **If valid**: Game is saved to database
6. **User redirected** to games list
7. **If invalid**: Form shows errors

All of this was generated automatically! 🤯

## Next steps 🚀

Now you have a fully functional game management system! In the next chapters, we can:

- Make the interface even more beautiful
- Add search and filtering
- Upload game cover images
- Add statistics and charts

But take a moment to appreciate what you've built. You now have:
- User authentication ✅
- Database storage ✅  
- Complete CRUD operations ✅
- Professional web interface ✅

That's a real web application! 🎉

:::tip[Keep experimenting!]
- Try adding games with different statuses
- Test the edit and delete functions
- Create multiple user accounts and see how each has their own collection
- Look at the generated code (but don't worry if it's complex!)
:::

Ready to add file upload functionality? Let's move on to **[File Upload](/framefox/quicklaunch/file-upload)**! 🚀✨

from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from datetime import datetime
from forms import EquipmentForm, RegisterForm, LoginForm, MaterialsForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from fpdf import FPDF
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


# Table for books
class Equipments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    quantity = db.Column(db.Integer)
    marca = db.Column(db.Integer)
    date = db.Column(db.String(250))


class Materials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    quantity = db.Column(db.Integer)
    marca = db.Column(db.Integer)
    date = db.Column(db.String(250))


# Table for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    email = db.Column(db.String(250), unique=True)
    marca = db.Column(db.String(250))
    funct = db.Column(db.String(250))
    telephone = db.Column(db.String(250))
    password = db.Column(db.String(250))


# Table for user cart
class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_cart = db.Column(db.Integer)
    item_name = db.Column(db.String(250))
    item_quantity = db.Column(db.Integer)
    date_item_added = db.Column(db.String(250))


db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    print(f'User id to load: {User.query.get(int(user_id))}')
    return User.query.get(int(user_id))


#################################################                         ################################################################
#################################################                         ################################################################
#################################################                         ################################################################

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        try:
            preview = db.session.query(Equipments).all()[:]  # ca sa vad doar primele N elemente
        except:
            preview = []
        # print(f'Logged in user ? {current_user.is_authenticated}')
        # print(f'Current user: {current_user},{current_user}')
    elif request.method == 'POST':
        selected_user = request.form['nume']
        print(f'The current user after the change is :{current_user.name}')
        return render_template('index.html', selected_user=current_user)
    return render_template("index.html", content=preview, users=db.session.query(User))


@app.route('/equipments', methods=['GET', 'POST'])
def equipments():
    if request.method == 'GET':
        try:
            content = db.session.query(Equipments).all()  # ca sa vad doar primele N elemente
        except:
            content = []
        # print(f'Logged in user ? {current_user.is_authenticated}')
        # print(f'Current user: {current_user},{current_user}')
    elif request.method == 'POST':
        selected_user = request.form['nume']
        print(f'The current user after the change is :{current_user.name}')
        return render_template('equipments.html', selected_user=current_user)
    return render_template("equipments.html", content=content, users=db.session.query(User))


@app.route('/materials', methods=['GET', 'POST'])
def materials():
    if request.method == 'GET':
        try:
            content = db.session.query(Materials).all()  # ca sa vad doar primele N elemente
        except:
            content = []
        # print(f'Logged in user ? {current_user.is_authenticated}')
        # print(f'Current user: {current_user},{current_user}')
    elif request.method == 'POST':
        selected_user = request.form['nume']
        print(f'The current user after the change is :{current_user.name}')
        return render_template('materials.html', selected_user=current_user)
    return render_template("materials.html", content=content, users=db.session.query(User))


@app.route('/change_user', methods=['POST'])
def change_user():
    username = request.form['nav-link']
    user = User.query.filter_by(name=username).first()
    login_user(user)
    flash(f'Ai schimbat cu succes in inventarul: {username}', 'success')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    error = None
    register_user_form = RegisterForm()
    if request.method == 'POST':
        # checking for email if already exists
        if User.query.filter_by(email=register_user_form.email.data).first():
            error = 'Adresa de email deja folosita. Incearca o noua adresa.'
            return render_template('register.html', form=register_user_form, error=error)

        elif register_user_form.validate_on_submit():

            ###vezi ca aici tre sa modifici parola pt cont de admin
            # elif register_user_form.validate_on_submit() and \
            #         register_user_form.password.data == register_user_form.password_confirmation.data:  # match both passwords
            #     # hash password
            #     print(register_user_form.password.data)
            #
            #     hash_password = generate_password_hash(password=register_user_form.password.data, method='pbkdf2:sha256',
            #                                            salt_length=8)
            # print(hash_password)

            new_user = User(name=register_user_form.name.data,
                            marca=register_user_form.marca.data,
                            funct=register_user_form.funct.data,
                            telephone=register_user_form.telephone.data,
                            email=register_user_form.email.data,
                            password='NULL',
                            )
            db.session.add(new_user)
            db.session.commit()

            # Log in and authenticate user after adding details to database
            login_user(new_user)
            return redirect(url_for('catalogue'))

    return render_template('register.html', form=register_user_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        # search for the account
        if User.query.filter_by(email=str(login_form.email.data)).first():
            # if the account is registered
            user_to_login = User.query.filter_by(email=login_form.email.data).first()

            # checking for password
            if user_to_login.password == login_form.password.data:
                # if check_password_hash(pwhash=user_to_login.password, password=login_form.password.data):
                flash('Te-ai logat cu succes in contul de admin!')

                # Log in and authenticate user
                login_user(user_to_login)
                print(f"Current user: {current_user, current_user.id, current_user.name}")
                return redirect(url_for('index'))
            else:
                error = 'Invalid password,please try again.'
                return render_template('login.html', error=error, form=login_form)
        else:
            error = "That email does not exist, please try again."
            return render_template('login.html', error=error, form=login_form)

    return render_template('login.html', form=login_form)


@app.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    edit_form = EquipmentForm()
    if request.method == 'GET':
        ###aici identific cartea din db si ii preiau caracteristicile pt editare
        item_to_edit = Equipments.query.filter_by(id=id).first()
        # print('GET')
        edit_form.name.data = item_to_edit.name
        edit_form.quantity.data = item_to_edit.quantity
        edit_form.marca.data = item_to_edit.marca
        return render_template('edit.html', form=edit_form)

    # Submit changes to db
    elif request.method == 'POST':
        if edit_form.validate_on_submit():
            # Enter new data in db
            edited_equipment = Equipments.query.filter_by(id=id).first()
            edited_equipment.name = edit_form.name.data
            edited_equipment.quantity = edit_form.quantity.data
            edited_equipment.marca = edit_form.marca.data
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('edit.html', form=edit_form)


@app.route('/add_equipment', methods=['POST', "GET"])
def add_equipment():
    add_equipment_form = EquipmentForm()
    if request.method == 'POST':
        # add a new item to the db
        if add_equipment_form.validate_on_submit():
            new_equipment = Equipments(marca=add_equipment_form.marca.data,
                                       name=add_equipment_form.name.data,
                                       quantity=add_equipment_form.quantity.data,
                                       date=datetime.now().strftime('%x')
                                       )
            db.session.add(new_equipment)
            db.session.commit()

            return redirect(url_for('equipments'))
        return render_template('add_equipment.html', form=add_equipment_form)
    else:
        return render_template('add_equipment.html', form=add_equipment_form)


@app.route('/add_material', methods=['POST', "GET"])
def add_material():
    add_materials_form = MaterialsForm()
    if request.method == 'POST':
        # add a new item to the db
        if add_materials_form.validate_on_submit():
            new_equipment = Materials(marca=add_materials_form.marca.data,
                                      name=add_materials_form.name.data,
                                      quantity=add_materials_form.quantity.data,
                                      date=datetime.now().strftime('%x')
                                      )
            db.session.add(new_equipment)
            db.session.commit()

            return redirect(url_for('materials'))
        return render_template('add_material.html', form=add_materials_form)
    else:
        return render_template('add_material.html', form=add_materials_form)


@app.route('/delete/<int:id>', methods=["GET", "POST"])
def delete_book(id):
    equipment_to_delete = Equipments.query.get(id)
    db.session.delete(equipment_to_delete)
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/catalogue")
def catalogue():
    requested_post = None
    all_equipment = db.session.query(Equipments).all()
    return render_template("catalogue.html", content=all_equipment, date=datetime.now().strftime("%d/%m/%Y"))


@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    # get the page the request came from
    page = request.form['page']
    if page == 'materials':
        print('MATERIALE')
        item_to_add = ShoppingCart(user_cart=int(current_user.id),
                                   item_name=Materials.query.filter_by(id=id).first().name,
                                   item_quantity=int(request.form['quantity']),
                                   date_item_added=datetime.now().strftime('%x'))
        print(int(request.form['quantity']))

        # Check if the quantity key exists in the request.form dictionary
        if 'quantity' in request.form:
            item_to_add.item_quantity = int(request.form['quantity'])
        else:
            # Handle the case where the quantity key is missing
            item_to_add.item_quantity = 'quantity missing'
        db.session.add(item_to_add)
        db.session.commit()

        # Substract from the storage
        equipment = Materials.query.filter_by(id=id).first()
        equipment.quantity = equipment.quantity - item_to_add.item_quantity
        db.session.commit()
        return redirect(url_for('materials'))

    elif page == 'equipments':
        print('ECHIPAMENTE')
        item_to_add = ShoppingCart(user_cart=int(current_user.id),
                                   item_name=Equipments.query.filter_by(id=id).first().name,
                                   item_quantity=int(request.form['quantity']),
                                   date_item_added=datetime.now().strftime('%x'))
        print(int(request.form['quantity']))

        # Check if the quantity key exists in the request.form dictionary
        if 'quantity' in request.form:
            item_to_add.item_quantity = int(request.form['quantity'])
        else:
            # Handle the case where the quantity key is missing
            item_to_add.item_quantity = 'quantity missing'
        db.session.add(item_to_add)
        db.session.commit()

        # Substract from the storage
        equipment = Equipments.query.filter_by(id=id).first()
        equipment.quantity = equipment.quantity - item_to_add.item_quantity
        db.session.commit()
        return redirect(url_for('equipments'))

    else:
        return redirect(url_for('index'))


@app.route('/inventory')
@login_required
def inventory():
    # get all items added by a user , but in a list structure
    lst = ShoppingCart.query.filter_by(user_cart=int(current_user.id)).all()
    return render_template('inventory.html', inventory=lst)


@app.route('/personal-raport')
def personal_report():
    id = (User.query.filter_by(name=current_user.name).first()).id
    inventory = ShoppingCart.query.filter_by(id=id).first()

    # get all the titles added by a user , but in a list structure

    lst = ShoppingCart.query.filter_by(id=id).all()
    print(f'ALL {ShoppingCart.query.filter_by(id=id).all()}')

    # search for every title from the list above in the Books table and add them in a list
    # name = [Books.query.filter_by(name=item.book_name).first() for item in lst]
    lst = ShoppingCart.query.filter_by(user_cart=int(current_user.id)).all()
    lst=[item for item in lst if item.date_item_added==datetime.now().strftime('%x')]

    pdf = FPDF(format='A4', orientation='p', unit='mm')
    # Create the page
    pdf.add_page()
    # Header content
    pdf.set_font(family='Times', size=30, style='B')
    pdf.cell(w=20, h=12, txt=f'Preluare de echipament ', align='L', ln=1, border=0)
    pdf.ln(4)
    pdf.set_font(family='Times', size=16, style='B')
    pdf.cell(w=20, h=12, txt=f'Data: {datetime.now().strftime("%m/%d/%Y")}', align='L', ln=1, border=0)
    pdf.set_font(family='Times', size=18, style='I')
    pdf.cell(w=20, h=12, txt=f'Subsemnatul {current_user.name.title()}, '
                             f'a preluat urmatoarele materiale.', align='L', ln=1, border=0)
    pdf.ln(12)
    # Columns hdr
    pdf.set_font(family='Times', size=14, style='B')
    pdf.cell(w=100, h=12, txt='Echipament', align='C', ln=0, border=1)
    pdf.cell(w=40, h=12, txt='Cantitate', align='C', ln=0, border=1)
    pdf.cell(w=40, h=12, txt='Data', align='C', ln=1, border=1)
    for item in lst:
        # Table content
        pdf.set_font(family='Times', size=12)
        pdf.cell(w=100, h=12, txt=item.item_name, align='C', ln=0, border=1)
        pdf.cell(w=40, h=12, txt=f"{str(item.item_quantity)} Buc.", align='C', ln=0, border=1)
        pdf.cell(w=40, h=12, txt=f"{str(item.date_item_added)} ", align='C', ln=0, border=1)
        pdf.ln(12)
    # # Adding the total
    # pdf.set_font(family='Times', size=12, style='B')
    # pdf.cell(w=100, h=12, txt='', align='C', ln=0, border=1)
    # pdf.cell(w=40, h=12, txt='', align='C', ln=0, border=1)
    # pdf.cell(w=40, h=12, txt=str(total_sum), align='C', ln=0, border=1)
    # pdf.ln(20)
    # #
    # # Creating the sum sentence
    # pdf.set_font(family='Times', size=18, style='B')
    # pdf.cell(w=0, h=12, txt=f'The total due amont is {total_sum} Eur', align='L', ln=1, border=0)

    # Creating the name of the file
    pdf.output('static/files/invoice.pdf')
    return send_from_directory(directory=app.static_folder, path='files/invoice.pdf', as_attachment=True)


@app.route('/search', methods=["GET", "POST"])
def search():
    results = []
    if request.method == 'POST':
        print(request.form['searchbox'])
    search = request.form['searchbox']

    # item searched in equipments table
    all_items = db.session.query(Equipments).all()
    for equipment in all_items:
        if str(search.lower()) in equipment.name.lower():
            equipment.type = 'equipment'
            results.append(equipment)
        elif str(search.lower()) in str(equipment.marca):
            equipment.type = 'equipment'
            results.append(equipment)
        else:
            result = None

    # item searched in materials table
    all_items = db.session.query(Materials).all()
    for material in all_items:
        if str(search.lower()) in material.name.lower():
            material.type = 'material'
            results.append(material)
        elif str(search.lower()) in str(material.marca):
            material.type = 'material'
            results.append(material)
        else:
            result = None

    return render_template('search.html', items=results, date=datetime.now().strftime("%d/%m/%Y"))


@app.route('/return_item/<int:id>', methods=["GET", "POST"])
def return_item(id):
    item_name = request.form.get('name')
    quantity = int(request.form.get('quantity'))

    print(f'Returned {quantity} units of {item_name}')
    # add the item to the db - store
    if Equipments.query.filter_by(name=item_name).first():
        equipment_returned = Equipments.query.filter_by(name=item_name).first()
        Equipments.query.filter_by(name=item_name).first().quantity = equipment_returned.quantity + quantity
        print(equipment_returned)

        # # delete from the staff inventory
        update_inventory = ShoppingCart.query.filter_by(id=id).first()
        remaining_quantity = int(update_inventory.item_quantity) - quantity
        update_inventory.item_quantity = remaining_quantity
        db.session.commit()

    elif Materials.query.filter_by(name=item_name).first():
        equipment_returned = Materials.query.filter_by(name=item_name).first()
        Materials.query.filter_by(name=item_name).first().quantity = equipment_returned.quantity + quantity
        print(equipment_returned)

        # # delete from the staff inventory
        update_inventory = ShoppingCart.query.filter_by(id=id).first()
        remaining_quantity = int(update_inventory.item_quantity) - quantity
        update_inventory.item_quantity = remaining_quantity
        db.session.commit()

    # if de remaining items of a sort == 0, delete the db row
    if remaining_quantity == 0:
        db.session.delete(update_inventory)
        db.session.commit()

    return redirect(url_for('inventory'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def update_db():
    data = pd.read_excel('instance/stoc.XLSX')
    index_row = len(data['Material'])

    ###if there is already a 'Material' table , clear it and prep for new writing

    for index in range(index_row):
        new_material = Materials(name=data['Descriere material'][index],
                                 marca=float(data['Material'][index]),
                                 quantity=float(data['Fără restr.'][index]),
                                 date=datetime.now().strftime('%x'))
        db.session.add(new_material)
        db.session.commit()


# update_db()
@app.route('/update')
def update():
    update_db()
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)

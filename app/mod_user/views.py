# app/mod_user/views.py

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request, Response
from flask_login import login_user, logout_user, \
    login_required

from app import flask_bcrypt
from app.mod_main.views import confirm_email
from app.models import User, Email
from app.mod_user.forms import LoginForm

import os

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

user_blueprint = Blueprint('user', __name__,)

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.environ["SIB_APIKEY"]
lists_api_instance = sib_api_v3_sdk.ListsApi(sib_api_v3_sdk.ApiClient(configuration))


@user_blueprint.route('/albastru435', methods=['GET', 'POST'])
def login():
    """Login page for admins."""
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and flask_bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            flash('You are logged in. Welcome!', 'success')
            return redirect(url_for('user.admin'))
        else:
            flash('Invalid email and/or password.', 'danger')
            return render_template('user/login.html', form=form)
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out. Bye!', 'success')
    return redirect(url_for('main.index'))


@user_blueprint.route('/admin')
@login_required
def admin():
    """Displays submitted emails to the admin."""
    list_id = 5
    api_response = lists_api_instance.get_contacts_from_list(list_id)
    contacts_list = api_response.contacts
    signups = [e["email"] for e in contacts_list]
    # signups = Email.query.all()
    return render_template('user/admin.html', signups=signups)


@user_blueprint.route('/embed-code')
@login_required
def embed_code():
    """Displays ajax based form for easy copy and paste."""
    return render_template('user/embed-code.html')


@user_blueprint.route('/download-emails')
@login_required
def download_emails():
    """Downloads emails."""
    # signups = Email.query.all()
    signups = Email.query.filter_by(confirmed = True)

    def generate_csv():
        for e in signups:
            yield ','.join([e.email, str(e.email_added_on)])+'\n'

    response = Response(generate_csv(), mimetype='text/csv')
    response.headers.set(
        'Content-Disposition', 'attachment', filename='emails.csv')
    return response

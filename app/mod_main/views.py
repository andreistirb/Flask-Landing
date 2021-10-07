# app/mod_main/views.py

from app.token import confirm_token, generate_confirmation_token
from app.email import send_email
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask import Markup
import os

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.mod_main.forms import SignUpForm
from app import db
from app.models import Email

import datetime

main_blueprint = Blueprint('main', __name__,)
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.environ["SIB_APIKEY"]
contacts_api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
lists_api_instance = sib_api_v3_sdk.ListsApi(sib_api_v3_sdk.ApiClient(configuration))

@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Landing page for users to enter emails."""
    form = SignUpForm(request.form)
    if form.validate_on_submit():
        email_address = form.email.data
        # check if confirmed
        list_id = 5
        try:
            api_response = lists_api_instance.get_contacts_from_list(list_id)
            contacts_list = api_response.contacts
            emails_list = [e["email"] for e in contacts_list]
            if email_address in emails_list:
                flash('You have already subscribed, thank you!', 'success')
            else:
                # check if subscribed but not confirmed
                list_id = 4
                try:
                    api_response = lists_api_instance.get_contacts_from_list(list_id)
                    contacts_list = api_response.contacts
                    emails_list = [e["email"] for e in contacts_list]

                    if email_address in emails_list:
                        flash("Subscribed but not confirmed email. Please check your inbox for confirmation email", 'success')
                    # not subscribed, create new entry
                    else:
                        contact_to_create = sib_api_v3_sdk.CreateContact(email=email_address, list_ids=[4])
                        try:
                            contact_create_api_response = contacts_api_instance.create_contact(contact_to_create)
                            print(contact_create_api_response)
                        except ApiException as e:
                            print("Exception when calling ContactsApi -> create_contact: {}".format(e))
                        flash("Thank you for subscribing! Check your inbox for confirmation email", 'success')
                    
                except ApiException as e:
                    print("Exception when calling ListsApi -> get_contacts_from_list {}".format(e))

            
        except ApiException as e:
            print("Exceptions when calling listsAPI -> get_contacts_from_list {}".format(e))
        # test = Email.query.filter_by(email=form.email.data, source=None).first()
        # if test:
        #     # check if email is confirmed
        #     if test.confirmed:
        #     else:
        #         token = generate_confirmation_token(form.email.data)
        #         confirm_url = url_for('main.confirm_email', token=token, _external=True)
        #         html = render_template('email.html', confirm_url=confirm_url)
        #         subject = "Please confirm your subscription to ImgUpscale.com"
        #         send_email(form.email.data, subject, html)
        #         flash(Markup("email not confirmed, we have sent you another mail for confirmation"), 'success')
        # else:
        #     email = Email(email=form.email.data, confirmed=False)
        #     db.session.add(email)
        #     db.session.commit()
        #     flash('Thank you for your interest! Please check your inbox for confirmation email!', 'success')
        #     token = generate_confirmation_token(form.email.data)
        #     confirm_url = url_for('main.confirm_email', token=token, _external=True)
        #     html = render_template('email.html', confirm_url=confirm_url)
        #     subject = "Please confirm your subscription to ImgUpscale.com"
        #     send_email(form.email.data, subject, html)

        return redirect(url_for('main.index'))
    return render_template('main/index.html', form=form)

@main_blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired', 'danger')

    email_ = Email.query.filter_by(email=email).first()
    if email_.confirmed:
        flash('Email already confirmed! Thank you!')
    else:
        email_.confirmed = True
        email_.confirmed_on = datetime.datetime.now()
        db.session.add(email_)
        db.session.commit()
        flash('You have confirmed your account! Thank you!')
        # TODO send welcome email (create nice template)

    return redirect(url_for('main.index'))


@main_blueprint.route('/privacy_policy')
def privacy_policy():
    return render_template('main/privacy_policy.html')

@main_blueprint.route('/subscription_confirmed')
def subscription_confirmed():
    return render_template('main/subscription_confirmed.html')
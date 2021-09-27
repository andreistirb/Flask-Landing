# app/mod_main/views.py

from app.token import confirm_token, generate_confirmation_token
from app.email import send_email
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask import Markup

from app.mod_main.forms import SignUpForm
from app import db
from app.models import Email

import datetime

main_blueprint = Blueprint('main', __name__,)


@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Landing page for users to enter emails."""
    form = SignUpForm(request.form)
    if form.validate_on_submit():
        test = Email.query.filter_by(email=form.email.data, source=None).first()
        if test:
            # check if email is confirmed
            if test.confirmed:
                flash('You have already subscribed, thank you!', 'success')
            else:
                token = generate_confirmation_token(form.email.data)
                confirm_url = url_for('main.confirm_email', token=token, _external=True)
                html = render_template('email.html', confirm_url=confirm_url)
                subject = "Please confirm your subscription to ImgUpscale.com"
                send_email(form.email.data, subject, html)
                flash(Markup("email not confirmed, we have sent you another mail for confirmation"), 'success')
        else:
            email = Email(email=form.email.data, confirmed=False)
            db.session.add(email)
            db.session.commit()
            flash('Thank you for your interest! Please check your inbox for confirmation email!', 'success')
            token = generate_confirmation_token(form.email.data)
            confirm_url = url_for('main.confirm_email', token=token, _external=True)
            html = render_template('email.html', confirm_url=confirm_url)
            subject = "Please confirm your subscription to ImgUpscale.com"
            send_email(form.email.data, subject, html)

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
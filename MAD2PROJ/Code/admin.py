from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin ,Sector , Industry,AdCampaign,Sponcer ,Industry,Influencer# Assuming Admin model is defined in models.py
from tasks import accept_sponcer, reject_sponcer
admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

@admin.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = Admin.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('admin.register'))

        new_admin = Admin(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(new_admin)
        db.session.commit()
        flash('Registration successful, please log in')
        return redirect(url_for('admin.login'))

    return render_template('admin_register.html')

@admin.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        admin = Admin.query.filter_by(email=email).first()

        if not admin or not check_password_hash(admin.password, password):
            flash('Invalid credentials')
            return redirect(url_for('admin.login'))

        session['admin_id'] = admin.id  # Store admin ID in session
        session['admin_username'] = admin.username  # Store admin username in session
        flash('Login successful', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_login.html')

@admin.route('/dashboard')
def dashboard():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin_username = session['admin_username']
        sectors = Sector.query.all()
        industries = Industry.query.all()

        # Fetch unapproved sponsors
        unapproved_sponcers = Sponcer.query.filter_by(is_approved=False).all()

        # Fetch counts for active influencers, sponsors, and total ad campaigns
        active_influencers_count = Influencer.query.count()
        active_sponcers_count = Sponcer.query.filter_by(is_approved=True).count()
        total_ad_campaigns_count = AdCampaign.query.count()

        return render_template('admin_dashboard.html', 
                               admin_username=admin_username,
                               sectors=sectors,
                               industries=industries,
                               unapproved_sponcers=unapproved_sponcers,
                               active_influencers_count=active_influencers_count,
                               active_sponcers_count=active_sponcers_count,
                               total_ad_campaigns_count=total_ad_campaigns_count)
    else:
        flash('You need to login first.', 'warning')
        return redirect(url_for('admin.login'))

    
@admin.route('/logout')
def logout():
    session.pop('admin_id', None)  # Remove admin ID from session
    session.pop('admin_username', None)  # Remove admin username from session
    flash('You have been logged out', 'info')
    return redirect(url_for('admin.login'))

@admin.route('/add_sector', methods=['POST'])
def add_sector():
    sector_name = request.form.get('sector_name')
    new_sector = Sector(name=sector_name)
    db.session.add(new_sector)
    db.session.commit()
    flash('Sector added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/delete_sector/<int:sector_id>')
def delete_sector(sector_id):
    sector = Sector.query.get_or_404(sector_id)
    db.session.delete(sector)
    db.session.commit()
    flash('Sector deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/add_industry', methods=['POST'])
def add_industry():
    industry_name = request.form.get('industry_name')
    new_industry = Industry(name=industry_name)
    db.session.add(new_industry)
    db.session.commit()
    flash('Industry added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/delete_industry/<int:industry_id>')
def delete_industry(industry_id):
    industry = Industry.query.get_or_404(industry_id)
    db.session.delete(industry)
    db.session.commit()
    flash('Industry deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/view_ad_campaigns')
def view_ad_campaigns():
    if 'admin_id' in session:
        # Assuming you have an Admin model and using its ID to authenticate
        admin_id = session['admin_id']
        admin_username = session['admin_username']

        # Fetch all ad campaigns
        ad_campaigns = AdCampaign.query.all()

        return render_template('adminad_campaigns.html', admin_username=admin_username, ad_campaigns=ad_campaigns)
    else:
        flash('You need to login first.', 'warning')
        return redirect(url_for('admin.login'))



@admin.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    if 'admin_id' in session:
        campaign = AdCampaign.query.get_or_404(campaign_id)
        db.session.delete(campaign)
        db.session.commit()
        flash('Ad campaign deleted successfully.', 'success')
        return redirect(url_for('admin.view_ad_campaigns'))
    else:
        flash('You need to login first.', 'warning')
        return redirect(url_for('admin.login'))


@admin.route('/accept_sponcer/<int:sponcer_id>', methods=['POST'])
def accept_sponcer(sponcer_id):
    sponcer = Sponcer.query.get_or_404(sponcer_id)
    sponcer.is_approved = True
    db.session.commit()
    flash('Sponsor accepted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/reject_sponcer/<int:sponcer_id>', methods=['POST'])
def reject_sponcer(sponcer_id):
    sponcer = Sponcer.query.get_or_404(sponcer_id)
    db.session.delete(sponcer)
    db.session.commit()
    flash('Sponsor rejected and deleted.', 'success')
    return redirect(url_for('admin.dashboard'))

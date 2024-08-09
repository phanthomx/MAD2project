from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import Sponcer, Industry, CompanyIndustryAssociation ,db ,SponcerSocialMediaLink,AdCampaign, Sector, Influencer, Post,InfluencerSectorAssociation , AdRequest,ChatMessage
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import cloudinary
from datetime import datetime
from datetime import date
from flask_mail import Message
import csv
from io import StringIO
from flask import Response
from flask import Flask, render_template, redirect, url_for, session, flash, make_response
import csv
from io import StringIO
from flask import request, redirect, url_for, flash, session
from flask_mail import Message
from extensions import mail

cloudinary.config(
    cloud_name='ddfzdi2py',
    api_key='986259854125851',
    api_secret='28xQ1ArAeUMSOurgBLBirOz_nR8'
)

sponcer = Blueprint("sponcer", __name__, static_folder="static", template_folder="templates")
# sponcer.py

  # Import mail from extensions

sponcer = Blueprint("sponcer", __name__, static_folder="static", template_folder="templates")

@sponcer.route('/send_ad_request/<string:influencer_id>', methods=['POST'])
def send_ad_request(influencer_id):
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))
    
    sponcer_id = session['sponcer_id']
    campaign_id = request.form.get('campaign_id')
    price = request.form.get('price')
    
    if not campaign_id or not price:
        flash('Campaign and price are required.', 'danger')
        return redirect(url_for('sponcer.influencer_profile', influencer_id=influencer_id))
    
    # Create and save the ad request
    ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        sponcer_id=sponcer_id,
        price=price,
        status='Pending'
    )
    
    db.session.add(ad_request)
    db.session.commit()

    # Send email to the influencer
    influencer = Influencer.query.get(influencer_id)
    if influencer and influencer.email:
        # Email details
        msg = Message(
            "New Ad Request",
            sender="athenamcgonagall7@gmail.com",
            recipients=[influencer.email]
        )
        
        # Customize the email body
        msg.body = f"Dear {influencer.name},\n\nYou have received a new ad request for the campaign.\nThe proposed price is: {ad_request.price}.\n\nPlease review the request in your dashboard.\n\nBest regards,\nYour Team"
        
        # Use the mail instance from the current app context
        with current_app.app_context():
            mail.send(msg)
    
    flash('Ad request sent successfully, and email notification sent to the influencer.', 'success')
    return redirect(url_for('sponcer.influencer_profile', influencer_id=influencer_id))

@sponcer.route("/", methods=['GET', 'POST'])
def sponlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database for the sponsor by username
        sponcer = Sponcer.query.filter_by(username=username).first()

        # Check if sponsor exists, password is correct, and sponsor is approved
        if sponcer and check_password_hash(sponcer.password, password):
            if sponcer.is_approved:
                session['sponcer_id'] = sponcer.id
                flash('Login successful!', 'success')
                return redirect(url_for('sponcer.dashboard'))
            else:
                flash('Your account is not yet approved. Please wait for approval.', 'warning')
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    
    return render_template('sponlogin.html')


@sponcer.route("/registration", methods=['GET', 'POST'])
def sponregister():
    if request.method == 'POST':
        username = request.form['username']
        company_name = request.form['company_name']
        company_email = request.form['company_email']
        password = generate_password_hash(request.form['password'])
        description = request.form['description']
        profile_pic = request.files['profile_pic']

        new_sponcer = Sponcer(
            username=username,
            company_name=company_name,
            company_email=company_email,
            password=password,
            description=description
        )

        if profile_pic:
            upload_result = new_sponcer.upload_profile_pic(profile_pic)
            if not upload_result:
                flash('Error uploading profile picture', 'danger')
                return redirect(url_for('sponcer.sponregister'))

        try:
            db.session.add(new_sponcer)
            db.session.commit()
            flash('Sponsor registered successfully', 'success')
            return redirect(url_for('sponcer.sponlogin'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('sponcer.sponregister'))

    return render_template("sponregister.html")
 # adjust imports as needed

from datetime import datetime

from datetime import date

@sponcer.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))

    sponcer_id = session['sponcer_id']
    sponcer = Sponcer.query.get(sponcer_id)

    if not sponcer:
        flash('Sponsor not found.', 'danger')
        return redirect(url_for('sponcer.sponlogin'))

    # Fetch associated industries
    associations = CompanyIndustryAssociation.query.filter_by(company_id=sponcer_id).all()
    industries = [Industry.query.get(assoc.industry_id) for assoc in associations]
    all_industries = Industry.query.all()

    # Fetch social media links
    social_media_links = SponcerSocialMediaLink.query.filter_by(sponcer_id=sponcer_id).all()

    # Fetch ad campaigns
    ad_campaigns = AdCampaign.query.filter_by(sponcer_id=sponcer_id).all()

    if request.method == 'POST':
        # Adding a new industry
        new_industry_id = request.form.get('industry')
        if new_industry_id:
            existing_association = CompanyIndustryAssociation.query.filter_by(company_id=sponcer_id, industry_id=new_industry_id).first()
            if existing_association:
                flash('Industry already associated with the sponsor.', 'warning')
            elif len(industries) >= 3:
                flash('You can only associate up to 3 industries.', 'warning')
            else:
                new_association = CompanyIndustryAssociation(company_id=sponcer_id, industry_id=new_industry_id)
                db.session.add(new_association)
                db.session.commit()
                flash('Industry added successfully.', 'success')
                return redirect(url_for('sponcer.dashboard'))

        # Adding a new ad campaign
        if 'campaign_name' in request.form:
            campaign_name = request.form.get('campaign_name')
            campaign_description = request.form.get('campaign_description')
            campaign_start_date = request.form.get('campaign_start_date')
            campaign_end_date = request.form.get('campaign_end_date')
            campaign_budget = request.form.get('campaign_budget')
            campaign_picture = request.files.get('campaign_picture')

            # Convert date strings to datetime objects
            try:
                start_date = datetime.strptime(campaign_start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(campaign_end_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('sponcer.dashboard'))

            new_campaign = AdCampaign(
                sponcer_id=sponcer_id,
                name=campaign_name,
                description=campaign_description,
                start_date=start_date,
                end_date=end_date,
                budget=campaign_budget
            )
            if campaign_picture:
                new_campaign.upload_picture(campaign_picture)

            db.session.add(new_campaign)
            db.session.commit()
            flash('Ad campaign created successfully.', 'success')
            return redirect(url_for('sponcer.dashboard'))

    current_date = date.today()
    print(current_date)
    return render_template('spondashboard.html', sponcer=sponcer, industries=industries, all_industries=all_industries, social_media_links=social_media_links, ad_campaigns=ad_campaigns, current_date=current_date)

@sponcer.route('/logout')
def slogout():
    session.pop('sponsor_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('sponcer.sponlogin'))


@sponcer.route('/delete_industry/<int:industry_id>', methods=['POST'])
def delete_industry(industry_id):
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))
    
    sponcer_id = session['sponcer_id']
    association = CompanyIndustryAssociation.query.filter_by(company_id=sponcer_id, industry_id=industry_id).first()
    
    if association:
        db.session.delete(association)
        db.session.commit()
        flash('Industry removed successfully.', 'success')
    else:
        flash('Industry association not found.', 'danger')
    
    return redirect(url_for('sponcer.dashboard'))


@sponcer.route('/add_social_media_link', methods=['POST'])
def add_social_media_link():
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))
    
    sponcer_id = session['sponcer_id']
    username = request.form['username']
    platform_name = request.form['platform_name']
    link_to_page = request.form['link_to_page']
    
    new_link = SponcerSocialMediaLink(sponcer_id, username, platform_name, link_to_page)
    db.session.add(new_link)
    db.session.commit()
    
    flash('Social media link added successfully.', 'success')
    return redirect(url_for('sponcer.dashboard'))

@sponcer.route('/delete_social_media_link/<int:link_id>', methods=['POST'])
def delete_social_media_link(link_id):
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))
    
    link = SponcerSocialMediaLink.query.get(link_id)
    if link:
        db.session.delete(link)
        db.session.commit()
        flash('Social media link deleted successfully.', 'success')
    else:
        flash('Social media link not found.', 'danger')
    
    return redirect(url_for('sponcer.dashboard'))



@sponcer.route("/delete_campaign/<int:campaign_id>", methods=['POST'])
def delete_campaign(campaign_id):
    print("Deleting campaign with ID:", campaign_id)
    campaign = AdCampaign.query.get(campaign_id)
    if campaign:
        try:
            db.session.delete(campaign)
            db.session.commit()
            flash('Campaign deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    else:
        flash('Campaign not found', 'danger')
    return redirect(url_for('sponcer.dashboard'))


@sponcer.context_processor
def inject_today_date():
    return {'current_date': date.today()}



@sponcer.route('/search-posts', methods=['GET', 'POST'])
def searchposts():
    sectors = Sector.query.all()
    posts = []
    if request.method == 'POST':
        selected_sector_id = request.form['sector']
        posts = db.session.query(Post).join(Influencer).join(InfluencerSectorAssociation).filter(
            InfluencerSectorAssociation.sector_id == selected_sector_id).all()
    return render_template('showpost.html', sectors=sectors, posts=posts)

@sponcer.route('/influencer/<string:influencer_id>', methods=['GET', 'POST'])
def influencer_profile(influencer_id):
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))

    sponcer_id = session['sponcer_id']
    influencer = Influencer.query.get_or_404(influencer_id)
    social_media_links = influencer.social_media_links

    associations = InfluencerSectorAssociation.query.filter_by(influencer_id=influencer_id).all()
    sector_ids = [association.sector_id for association in associations]
    sectors = Sector.query.filter(Sector.id.in_(sector_ids)).all()

    posts = influencer.posts
    ad_campaigns = AdCampaign.query.filter_by(sponcer_id=sponcer_id).all()

    if request.method == 'POST':
        campaign_id = request.form.get('campaign_id')
        price = request.form.get('price')
        
        if campaign_id and price:
            new_request = AdRequest(
                campaign_id=campaign_id,
                influencer_id=influencer.id,
                sponcer_id=sponcer_id,
                price=price,
                status='Pending'
            )
            db.session.add(new_request)
            db.session.commit()
            flash('Ad request sent successfully.', 'success')
            return redirect(url_for('sponcer.influencer_profile', influencer_id=influencer.id))

    return render_template('showinfluencerpro.html', influencer=influencer, social_media_links=social_media_links, sectors=sectors, posts=posts, ad_campaigns=ad_campaigns)

# sponcer.py





@sponcer.route('/ad_campaigns/<int:campaign_id>/view_requests')
def view_requests(campaign_id):
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))

    campaign = AdCampaign.query.get_or_404(campaign_id)
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()

    return render_template('ad_requests.html', campaign=campaign, ad_requests=ad_requests)

@sponcer.route('/ad_requests/<int:request_id>/chat', methods=['GET', 'POST'])
def view_and_send_chats(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)

    if ad_request.sponcer_id != session.get('sponcer_id'):
        abort(403)  # Handle unauthorized access

    campaign = AdCampaign.query.get(ad_request.campaign_id)
    chats = ChatMessage.query.filter_by(ad_request_id=request_id).order_by(ChatMessage.timestamp.asc()).all()

    if request.method == 'POST':
        message = request.form.get('text')
        if message:
            new_chat_message = ChatMessage(
                ad_request_id=request_id,
                campaign_id=ad_request.campaign_id,
                sender_id=session.get('sponcer_id'),
                receiver_id=ad_request.influencer_id,
                text=message
            )
            db.session.add(new_chat_message)
            db.session.commit()
            flash('Message sent successfully.', 'success')
            return redirect(url_for('sponcer.view_and_send_chats', request_id=request_id))

    return render_template('view_chats.html', ad_request=ad_request, campaign=campaign, chats=chats)

@sponcer.route('/respond_ad_request/<int:request_id>/<string:response>', methods=['POST'])
def respond_ad_request(request_id, response):
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))

    ad_request = AdRequest.query.get_or_404(request_id)

    if ad_request.sponcer_id != session['sponcer_id']:
        flash('Unauthorized to respond to this ad request.', 'danger')
        return redirect(url_for('sponcer.dashboard'))

    if ad_request.status != 'Pending':
        flash('This ad request has already been responded to.', 'warning')
        return redirect(url_for('sponcer.view_requests', campaign_id=ad_request.campaign_id))

    try:
        if response == 'accept':
            ad_request.status = 'Accepted'
            db.session.commit()
            flash('Ad request accepted successfully.', 'success')
        elif response == 'reject':
            ad_request.status = 'Rejected'
            db.session.commit()
            flash('Ad request rejected successfully.', 'info')
        else:
            flash('Invalid response.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('sponcer.view_requests', campaign_id=ad_request.campaign_id))

@sponcer.route("/update_campaign", methods=['POST'])
def update_campaign():
    campaign_id = request.form.get('campaign_id')
    new_budget = request.form.get('new_budget')
    new_start_date = request.form.get('new_start_date')
    new_end_date = request.form.get('new_end_date')

    campaign = AdCampaign.query.get(campaign_id)
    if campaign:
        try:
            campaign.budget = float(new_budget)
            campaign.start_date = datetime.strptime(new_start_date, '%Y-%m-%d').date()
            campaign.end_date = datetime.strptime(new_end_date, '%Y-%m-%d').date()
            db.session.commit()
            flash('Campaign updated successfully.', 'success')
        except ValueError:
            flash('Invalid data format for budget or dates.', 'danger')
    else:
        flash('Campaign not found.', 'danger')

    return redirect(url_for('sponcer.dashboard'))


  # Update this import according to your project structure

@sponcer.route('/sponcer/export_campaigns', methods=['GET'])
def export_campaigns():
    if 'sponcer_id' not in session:
        flash('You need to login first.', 'warning')
        return redirect(url_for('sponcer.sponlogin'))

    sponcer_id = session['sponcer_id']
    ad_campaigns = AdCampaign.query.filter_by(sponcer_id=sponcer_id).all()

    # Prepare CSV content
    si = StringIO()
    writer = csv.writer(si)

    # Write headers
    writer.writerow(['Campaign Name', 'Description', 'Start Date', 'End Date', 'Budget'])

    # Write campaign data
    for campaign in ad_campaigns:
        writer.writerow([campaign.name, campaign.description, campaign.start_date, campaign.end_date, campaign.budget])

    # Generate a response with the CSV data
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=campaigns.csv"
    output.headers["Content-type"] = "text/csv"
    
    # Flash message or email alert to notify completion
    flash('Campaign export completed. Your file is downloading.', 'success')

    return output

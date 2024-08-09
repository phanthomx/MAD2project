from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from models import Influencer, Sector, Post, InfluencerSectorAssociation, PostSectorAssociation , db , SocialMediaLink ,AdRequest,Sponcer, Industry, CompanyIndustryAssociation ,db ,SponcerSocialMediaLink,AdCampaign,ChatMessage
from cloudinary.uploader import upload
from cloudinary import config as cloudinary_config
influencer = Blueprint("influencer", __name__, static_folder="static", template_folder="templates")


cloudinary_config(
    cloud_name='ddfzdi2py',
    api_key='986259854125851',
    api_secret='28xQ1ArAeUMSOurgBLBirOz_nR8'
)

@influencer.route("/registration", methods=["GET", "POST"])
def iregister():
    if request.method == "POST":
        # Handle form submission
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        bio = request.form['bio']
        profile_pic = request.files['profile_pic']
        
        new_influencer = Influencer(username=username, name=name, email=email, password=password, bio=bio)
        
        if profile_pic:
            upload_result = new_influencer.upload_profile_pic(profile_pic)
            if not upload_result:
                flash('Error uploading profile picture', 'danger')
                return redirect(url_for('influencer.iregister'))

        try:
            db.session.add(new_influencer)
            db.session.commit()
            flash('Influencer registered successfully', 'success')
            return redirect(url_for('influencer.ilogin'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('influencer.iregister'))

    return render_template("infregister.html")

@influencer.route("/", methods=["GET", "POST"])
def ilogin():
    if request.method == "POST":
        # Handle form submission
        username = request.form['uname']
        password = request.form['psw']
        
        # Query the database for the influencer
        influencer = Influencer.query.filter_by(username=username).first()
        
        if influencer and check_password_hash(influencer.password, password):
            # Password is correct, store user ID and username in session
            session['influencer_id'] = influencer.influencer_id
            session['username'] = influencer.username
            flash('Login successful', 'success')
            print("---------------logged-in-------------")
            return redirect(url_for('influencer.dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template("inflogin.html")

@influencer.route("/logout")
def ilogout():
    session.pop('influencer_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('influencer.ilogin'))

# @influencer.route("/dashboard")
# def dashboard():
#     if 'influencer_id' not in session:
#         flash('Please log in first', 'danger')
#         return redirect(url_for('influencer.ilogin'))

#     influencer_id = session['influencer_id']
#     influencer = Influencer.query.get(influencer_id)

#     if not influencer:
#         flash('Influencer not found', 'danger')
#         return redirect(url_for('influencer.ilogin'))

#     return render_template("indashboard.html", influencer=influencer)




@influencer.route('/dashboard')
def dashboard():
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash('Influencer not found', 'danger')
        return redirect(url_for('influencer.ilogin'))

    social_media_links = SocialMediaLink.query.filter_by(influencer_id=influencer_id).all()
    influencer_sectors = db.session.query(Sector).join(InfluencerSectorAssociation).filter(InfluencerSectorAssociation.influencer_id == influencer_id).all()
    all_sectors = Sector.query.all()
    all_posts = Post.query.filter_by(influencer_id=influencer_id).all()
    
    post_sectors = {}
    for post in all_posts:
        sectors = db.session.query(Sector).join(PostSectorAssociation).filter(PostSectorAssociation.post_id == post.id).all()
        post_sectors[post.id] = sectors

    return render_template("indashboard.html", influencer=influencer, influencer_sectors=influencer_sectors, all_sectors=all_sectors, all_posts=all_posts, post_sectors=post_sectors, social_media_links=social_media_links)


@influencer.route("/add_sectors", methods=["POST"])
def add_sectors():
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    selected_sectors = request.form.getlist('sectors')

    if selected_sectors:
        for sector_id in selected_sectors:
            existing_association = InfluencerSectorAssociation.query.filter_by(influencer_id=influencer_id, sector_id=sector_id).first()
            if not existing_association:
                new_association = InfluencerSectorAssociation(influencer_id=influencer_id, sector_id=sector_id)
                db.session.add(new_association)
        db.session.commit()
        flash('Sectors added successfully', 'success')
    else:
        flash('No sectors selected', 'warning')

    return redirect(url_for('influencer.dashboard'))


@influencer.route("/delete_sector/<int:sector_id>", methods=["POST"])
def delete_sector(sector_id):
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    association = InfluencerSectorAssociation.query.filter_by(influencer_id=influencer_id, sector_id=sector_id).first()

    if association:
        db.session.delete(association)
        db.session.commit()
        flash('Sector removed successfully', 'success')
    else:
        flash('Sector not found', 'warning')

    return redirect(url_for('influencer.dashboard'))


@influencer.route("/add_post", methods=["POST"])
def add_post():
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    description = request.form.get('description')
    media_file = request.files.get('media')
    post_sectors = request.form.getlist('post_sectors')

    if description and media_file:
        new_post = Post(influencer_id=influencer_id, description=description)
        if new_post.upload_media(media_file):
            db.session.add(new_post)
            db.session.commit()

            # Create associations with sectors
            for sector_id in post_sectors:
                association = PostSectorAssociation(post_id=new_post.id, sector_id=int(sector_id))
                db.session.add(association)
            db.session.commit()

            flash('Post added successfully', 'success')
        else:
            flash('Failed to upload media', 'danger')
    else:
        flash('Description and media are required', 'danger')

    return redirect(url_for('influencer.dashboard'))


@influencer.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    post = Post.query.filter_by(id=post_id, influencer_id=influencer_id).first()
    if not post:
        flash('Post not found', 'danger')
    else:
        # Delete associated sectors first
        PostSectorAssociation.query.filter_by(post_id=post.id).delete()
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully', 'success')

    return redirect(url_for('influencer.dashboard'))


@influencer.route("/add_social_media_link", methods=["POST"])
def add_social_media_link():
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    username = request.form.get('username')
    platform_name = request.form.get('platform_name')
    link_to_page = request.form.get('link_to_page')

    if username and platform_name and link_to_page:
        new_link = SocialMediaLink(influencer_id=influencer_id, username=username, platform_name=platform_name, link_to_page=link_to_page)
        db.session.add(new_link)
        db.session.commit()
        flash('Social media link added successfully', 'success')
    else:
        flash('Please fill in all fields', 'danger')

    return redirect(url_for('influencer.dashboard'))

@influencer.route('/delete_social_media_link/<int:link_id>', methods=['POST'])
def delete_social_media_link(link_id):
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    link = SocialMediaLink.query.get_or_404(link_id)

    if link.influencer_id != influencer_id:
        flash('You do not have permission to delete this link', 'danger')
        return redirect(url_for('influencer.dashboard'))

    db.session.delete(link)
    db.session.commit()

    flash('Social Media Link deleted successfully', 'success')
    return redirect(url_for('influencer.dashboard'))



@influencer.route('/ad-requests', methods=['GET', 'POST'])
def view_ad_requests():
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    influencer_id = session['influencer_id']
    ad_requests_received = AdRequest.query.filter_by(influencer_id=influencer_id).all()

    return render_template('influenceradreq.html', ad_requests_received=ad_requests_received)

@influencer.route('/update-ad-request-status/<int:request_id>', methods=['POST'])
def update_ad_request_status(request_id):
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    ad_request = AdRequest.query.get_or_404(request_id)
    new_status = request.form['status']

    if new_status in ['Accepted', 'Rejected', 'Pending']:
        ad_request.status = new_status
        db.session.commit()
        flash('Ad request status updated successfully', 'success')
    else:
        flash('Invalid status', 'danger')

    return redirect(url_for('influencer.view_ad_requests'))

@influencer.route('/sponcer/<int:sponcer_id>', methods=['GET'])
def sponcer_profile(sponcer_id):
    sponcer = Sponcer.query.get_or_404(sponcer_id)
    social_media_links = SponcerSocialMediaLink.query.filter_by(sponcer_id=sponcer_id).all()
    ad_campaigns = AdCampaign.query.filter_by(sponcer_id=sponcer_id).all()
    return render_template('sponcer_profileadd.html', sponcer=sponcer, social_media_links=social_media_links, ad_campaigns=ad_campaigns)


@influencer.route('/chat/<int:request_id>', methods=['GET', 'POST'])
def chat(request_id):
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    ad_request = AdRequest.query.get_or_404(request_id)
    chat_messages = ChatMessage.query.filter_by(ad_request_id=request_id).order_by(ChatMessage.timestamp.asc()).all()

    if request.method == 'POST':
        text = request.form['message']
        if text:
            new_message = ChatMessage(
                ad_request_id=request_id,
                campaign_id=ad_request.campaign_id,
                sender_id=session['influencer_id'],
                receiver_id=ad_request.sponcer_id,
                text=text
            )
            db.session.add(new_message)
            db.session.commit()
            # Redirect to the same chat page after adding the message
            return redirect(url_for('influencer.chat', request_id=request_id))

    return render_template('chat.html', ad_request=ad_request, chat_messages=chat_messages)

@influencer.route('/view-ad-campaigns', methods=['GET', 'POST'])
def view_ad_campaigns():
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    industries = Industry.query.all()
    ad_campaigns = []

    if request.method == 'POST':
        industry_id = request.form['industry_id']
        sponcer_ids = [association.company_id for association in CompanyIndustryAssociation.query.filter_by(industry_id=industry_id).all()]
        ad_campaigns = AdCampaign.query.filter(AdCampaign.sponcer_id.in_(sponcer_ids)).all()

        # Print image paths for debugging
        for campaign in ad_campaigns:
            print(f"Campaign ID: {campaign.id}, Image Path: {campaign.picture}")

    return render_template('view_ad_campaigns.html', industries=industries, ad_campaigns=ad_campaigns)

@influencer.route('/send_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
def send_ad_request(campaign_id):
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    campaign = AdCampaign.query.get_or_404(campaign_id)

    if request.method == 'POST':
        price = request.form.get('price')
        
        if not price:
            flash('Price is required.', 'danger')
            return redirect(url_for('influencer.send_ad_request', campaign_id=campaign_id))

        try:
            ad_request = AdRequest(
                influencer_id=session['influencer_id'],
                sponcer_id=campaign.sponcer_id,
                campaign_id=campaign_id,
                price=price,
                status='Pending'
            )
            db.session.add(ad_request)
            db.session.commit()
            flash('Ad request sent successfully', 'success')
            return redirect(url_for('influencer.view_ad_campaigns'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('influencer.send_ad_request', campaign_id=campaign_id))

    return render_template('send_ad_request.html', campaign=campaign)

@influencer.route('/view-sponsor-profile/<int:sponsor_id>', methods=['GET'])
def view_sponsor_profile(sponsor_id):
    if 'influencer_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('influencer.ilogin'))

    sponsor = Sponcer.query.get_or_404(sponsor_id)
    social_media_links = SponcerSocialMediaLink.query.filter_by(sponcer_id=sponsor_id).all()
    ad_campaigns = AdCampaign.query.filter_by(sponcer_id=sponsor_id).all()

    # Fetch associated industries
    associated_industries = Industry.query.join(CompanyIndustryAssociation).filter_by(company_id=sponsor_id).all()

    return render_template('view_sponsor_profile.html', sponsor=sponsor, social_media_links=social_media_links, ad_campaigns=ad_campaigns, associated_industries=associated_industries)

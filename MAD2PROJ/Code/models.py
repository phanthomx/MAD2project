import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text
from cloudinary.uploader import upload
from cloudinary import config as cloudinary_config  
from models import * 

# SQLAlchemy instance
db = SQLAlchemy()

# Cloudinary configuration
cloudinary_config(
    cloud_name='ddfzdi2py',
    api_key='986259854125851',
    api_secret='28xQ1ArAeUMSOurgBLBirOz_nR8'
)

from cloudinary.utils import cloudinary_url

class Influencer(db.Model):
    __tablename__ = 'influencers'
    influencer_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(200), nullable=True)  # Store Cloudinary public ID for profile pic
    
    posts = db.relationship('Post', backref='influencer', lazy=True)
    social_media_links = db.relationship('SocialMediaLink', backref='influencer', lazy=True)

    def __init__(self, username, name, email, password, bio):
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.bio = bio

    def upload_profile_pic(self, profile_pic_file):
        try:
            upload_result = upload(profile_pic_file)
            self.profile_pic = upload_result['public_id']
        except Exception as e:
            print(f"Error uploading profile picture to Cloudinary: {str(e)}")
            return False
        return True

    @property
    def profile_pic_url(self):
        if self.profile_pic:
            url, options = cloudinary_url(self.profile_pic)
            return url
        return None



class Sector(db.Model):
    __tablename__ = 'sectors'
    id = db.Column(db.Integer, primary_key=True ,nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

class InfluencerSectorAssociation(db.Model):
    __tablename__ = 'influencer_sector_association'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.String(36), db.ForeignKey('influencers.influencer_id'), nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectors.id'), nullable=False)

    def __init__(self, influencer_id, sector_id):
        self.influencer_id = influencer_id
        self.sector_id = sector_id

class SocialMediaLink(db.Model):
    __tablename__ = 'social_media_links'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.String(36), db.ForeignKey('influencers.influencer_id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    platform_name = db.Column(db.String(50), nullable=False)
    link_to_page = db.Column(db.String(200), nullable=False)

    def __init__(self, influencer_id, username, platform_name, link_to_page):
        self.influencer_id = influencer_id
        self.username = username
        self.platform_name = platform_name
        self.link_to_page = link_to_page


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.String(36), db.ForeignKey('influencers.influencer_id'), nullable=False)
    media_url = db.Column(db.String(200), nullable=True)  # Store Cloudinary public ID for media
    description = db.Column(db.Text, nullable=True)

    associations = db.relationship('PostSectorAssociation', backref='post', lazy=True)

    def __init__(self, influencer_id, description=None):
        self.influencer_id = influencer_id
        self.description = description

    def upload_media(self, media_file):
        try:
            upload_result = upload(media_file)
            self.media_url = upload_result['secure_url'] 
        except Exception as e:
            print(f"Error uploading media to Cloudinary: {str(e)}")
            return False
        return True



class PostSectorAssociation(db.Model):
    __tablename__ = 'post_sector_association'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectors.id'), nullable=False)

    def __init__(self, post_id, sector_id):
        self.post_id = post_id
        self.sector_id = sector_id




class Sponcer(db.Model):
    __tablename__ = 'sponcers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    company_email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    
    def __init__(self, username, company_name, company_email, password, description=None):
        self.username = username
        self.company_name = company_name
        self.company_email = company_email
        self.password = password
        self.description = description

    def upload_profile_pic(self, profile_pic_file):
        try:
            print(f"Uploading profile picture: {profile_pic_file.filename}")
            upload_result = upload(profile_pic_file)
            self.profile_pic = upload_result['public_id']
            print(f"Uploaded profile picture successfully: {self.profile_pic}")
        except Exception as e:
            print(f"Error uploading profile picture to Cloudinary: {str(e)}")
            return False
        return True

    @property
    def profile_pic_url(self):
        if self.profile_pic:
            url, options = cloudinary_url(self.profile_pic)
            return url
        return None

class Industry(db.Model):
    __tablename__ = 'industries'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

class CompanyIndustryAssociation(db.Model):
    __tablename__ = 'company_industry_association'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('sponcers.id'), nullable=False)
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=False)

    def __init__(self, company_id, industry_id):
        self.company_id = company_id
        self.industry_id = industry_id

class SponcerSocialMediaLink(db.Model):
    __tablename__ = 'sponcer_social_media_links'
    id = db.Column(db.Integer, primary_key=True)
    sponcer_id = db.Column(db.Integer, db.ForeignKey('sponcers.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    platform_name = db.Column(db.String(50), nullable=False)
    link_to_page = db.Column(db.String(200), nullable=False)

    def __init__(self, sponcer_id, username, platform_name, link_to_page):
        self.sponcer_id = sponcer_id
        self.username = username
        self.platform_name = platform_name
        self.link_to_page = link_to_page
        
class AdCampaign(db.Model):
    __tablename__ = 'ad_campaigns'
    id = db.Column(db.Integer, primary_key=True)
    sponcer_id = db.Column(db.Integer, db.ForeignKey('sponcers.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(255), nullable=True)  # Field to store picture URL or filename

    def __init__(self, sponcer_id, name, description, start_date, end_date, budget, picture=None):
        self.sponcer_id = sponcer_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.picture = picture

    def upload_picture(self, picture_file):
        try:
            print(f"Uploading campaign picture: {picture_file.filename}")
            upload_result = upload(picture_file)
            self.picture = upload_result['public_id']
            print(f"Uploaded campaign picture successfully: {self.picture}")
        except Exception as e:
            print(f"Error uploading campaign picture to Cloudinary: {str(e)}")
            return False
        return True

    @property
    def picture_url(self):
        if self.picture:
            url, options = cloudinary_url(self.picture)
            return url
        return None



class AdRequest(db.Model):
    __tablename__ = 'ad_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('ad_campaigns.id'), nullable=False)
    influencer_id = db.Column(db.String(36), db.ForeignKey('influencers.influencer_id'), nullable=False)
    sponcer_id = db.Column(db.Integer, db.ForeignKey('sponcers.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    
    campaign = db.relationship('AdCampaign', backref='ad_requests')
    sponcer = db.relationship('Sponcer', backref='ad_requests')
    influencer = db.relationship('Influencer', backref='ad_requests')

    def __init__(self, campaign_id, influencer_id, sponcer_id, price, status):
        self.campaign_id = campaign_id
        self.influencer_id = influencer_id
        self.sponcer_id = sponcer_id
        self.price = price
        self.status = status

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_requests.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('ad_campaigns.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    
    ad_request = db.relationship('AdRequest', backref='chat_messages')
    campaign = db.relationship('AdCampaign', backref='chat_messages')

    def __init__(self, ad_request_id, campaign_id, sender_id, receiver_id, text):
        self.ad_request_id = ad_request_id
        self.campaign_id = campaign_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.text = text


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
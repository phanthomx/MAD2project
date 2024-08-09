from worker import *
import time
from flask import Flask, render_template
from models import db, Sponcer,AdRequest,Influencer,AdCampaign
from flask_mail import Mail, Message
from flask_mail import Message
from flask_mail import Message
from jinja2 import Template
from extensions import mail 
from celery.schedules import crontab
from celery import shared_task

@shared_task(ignore_result=False)
def accept_sponcer(sponcer_id):
    try:
        sponcer = Sponcer.query.get(sponcer_id)
        if sponcer:
            sponcer.is_approved = True
            db.session.commit()
            # Notify the sponsor or perform additional actions if needed
    except Exception as e:
        # Handle exceptions or retries if needed
        print(f"Error accepting sponsor: {e}")

@shared_task(ignore_result=False)
def reject_sponcer(sponcer_id):
    try:
        sponcer = Sponcer.query.get(sponcer_id)
        if sponcer:
            db.session.delete(sponcer)
            db.session.commit()
            # Notify the sponsor or perform additional actions if needed
    except Exception as e:
        # Handle exceptions or retries if needed
        print(f"Error rejecting sponsor: {e}")
        
@shared_task(ignore_result=False)
def send_daily_email():
    
#     app = create_app()
#     with app.app_context():
#         mail = Mail(app)
        pending_requests = db.session.query(AdRequest).filter_by(status='Pending').all()
        
        for request in pending_requests:
            influencer = db.session.query(Influencer).get(request.influencer_id)
            if influencer and influencer.email:
                msg = Message(
                    "Pending Ad Request Reminder",
                    sender="athenamcgonagall7@gmail.com",
                    recipients=[influencer.email]
                )
                msg.body = f"Dear {influencer.name},\n\nYou have a pending ad request for the campaigns Please review and respond at your earliest convenience.\n\nBest regards,\nYour Team"
                mail.send(msg)

# Schedule the email task every evening at 6 PM IST
# celery_app.conf.beat_schedule = {
#     'send-daily-email': {
#         'task': 'send_daily_email',
#         'schedule': crontab(hour=4, minute=38),  # 6 PM IST = 12:30 PM UTC
#     },
# }
@shared_task(ignore_result=False)
def generate_monthly_report():
    sponsors = Sponcer.query.all()
    
    for sponsor in sponsors:
        campaigns = AdCampaign.query.filter_by(sponcer_id=sponsor.id).all()
        
        # Generate the report for each campaign
        campaign_data = []
        for campaign in campaigns:
            total_ad_requests = AdRequest.query.filter_by(campaign_id=campaign.id).count()
            campaign_data.append({
                'name': campaign.name,
                'description': campaign.description,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'budget': campaign.budget,
                'total_ad_requests': total_ad_requests
            })
        
        # Generate HTML content
        report_html = render_template(
            'monthly_report_template.html',
            sponsor=sponsor,
            campaigns=campaign_data
        )
        
        # Create email
        msg = Message(
            subject="Monthly Activity Report",
            sender="athenamcgonagall7@gmail.com",
            recipients=[sponsor.company_email],
        )
        msg.html = report_html
        
        # Send email
        mail.send(msg)
import os

# Set Vercel environment flag
os.environ['VERCEL'] = '1'

from boomboxd.wsgi import application

# This is needed for Vercel serverless functions
app = application 
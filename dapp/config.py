
#+-+-+-+-+-+-+-+-+-+-+-
# |h|o|b|g|o|b|l|.|i|n|
#+-+-+-+-+-+-+-+-+-+-+ ------------------------------------------------------------------
# @title  : config.py
# @notice : flask config for hobgobl.in
# @author : Maka
# @license: gnu gpl3
# -+-+-+-+-+-+-+-+-+-+ ------------------------------------------------------------------

from flask import Flask
from flask_flatpages import FlatPages

from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

from os import getenv as _get
from dotenv import load_dotenv as _load ; _load()

get_secret = lambda : _get('SECRET')

app                                         = Flask(__name__)
app.secret_key                              = get_secret()

app.config['FLATPAGES_AUTO_RELOAD']         = True
app.config['FLATPAGES_EXTENSION'  ]         = '.md'
app.config['FLATPAGES_ROOT'       ]         = 'content'
app.config['FLATPAGES_MARKDOWN_EXTENSIONS'] = [FencedCodeExtension(), TableExtension()]

POST_DIR                                    = 'blog/posts'
PAGE_DIR                                    = 'pages'
PROJ_DIR                                    = 'projects'

pages                                       = FlatPages(app)

# ----------------------------------------------------------------------------------------#
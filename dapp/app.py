#+-+-+-+-+-+-+-+-+-+-+-
#|h|o|b|g|o|b|l|.|i|n|
#+-+-+-+-+-+-+-+-+-+-+ ------------------
# @title  : app.py                      |
# @notice : app routing for hobgobl.in  |
# @author : Maka                        |
# @license: gnu gpl3                    |
# -+-+-+-+-+-+-+-+-+-+ ------------------------------------------------------------------------------

from flask import render_template, Response
import markdown
import emoji
from config import app
from contents import index_content, blog_content, bin_content, info_content, fetch_post
from typing import Text, Callable

# -- Content Filters
@app.template_filter('markdown')
def markdown_filter(text):
  return markdown.markdown(text, extensions=app.config['FLATPAGES_MARKDOWN_EXTENSIONS'])

@app.template_filter('emoji')
def emoji_filter(text):
  return emoji.emojize(text)

# -- Request Abstractions
def page(template : Text, content : Callable) -> Response:
  page = content()
  return render_template(template, heading=page.header, quote=page.quote, content=page.content)

post = lambda name : render_template('blog/post.html', post=fetch_post(name))

# -+-+-+-+-+-+-+-+-+-+ ------------------------------------------------------------------------------

#-- Landing Page
@app.route('/')
def index():
  return page('index.html', index_content)

# -- Blog Posts
@app.route('/blog')
def blog():
  return page('blog/posts.html', blog_content)

# --- Blog Post
@app.route('/blog/posts/<name>/')
def posts(name):
  return post(name)

#-- Projects Bin
@app.route('/bin')
def projects():
  return page('bin.html', bin_content)

#-- Contact Info
@app.route('/info')
def contact():
  return page('info.html', info_content)

#--
# -+-+-+-+-+-+-+-+-+-+ ------------------------------------------------------------------------------

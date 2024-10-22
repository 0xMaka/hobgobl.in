#_________________________
# Basic template renderer |
# -+-+-+-+-+-+-+-+-+-+ ---------------------------------------------------
from flask import Blueprint, render_template, abort                    # |
from jinja2 import TemplateNotFound                                    # |

render = Blueprint('index', __name__, template_folder='templates')     # |

@render.route('/', defaults={'page': 'index'})                         # |
@render.route('/<page>')
def show(page):
  try : return render_template(f'pages/{page}.html')                   # |
  except TemplateNotFound : abort(404)                                 # |
#______________________________________________________________________# /
# -+-+-+-+-+-+-+-+-+-+ --------------------------------------------------


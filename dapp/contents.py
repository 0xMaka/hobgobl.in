#+-+-+-+-+-+-+-+-+-+-+-
#|h|o|b|g|o|b|l|.|i|n|
#+-+-+-+-+-+-+-+-+-+-+ ------------------------
# @title  : content.py                        |
# @notice : content functions for hobgobl.in  |
# @author : Maka                              |
# @license: gnu gpl3                          |
# -+-+-+-+-+-+-+-+-+-+ -------------------------------------------------------------------------------------------------------

from config import pages, POST_DIR, PAGE_DIR, PROJ_DIR
from typing import NamedTuple, Text, Any #, List
#from typing_extensions import TypeAlias
import random  as _random

greet    = lambda : _random.choice([ 'Hacker', 'Goblin' ])
greeting = lambda : f'Welcome to the Hob, {greet()}'

# Data : TypeAlias = List[Text] | Text # servers py version doesn't support this, is not worth any gymnastics

# -+-+-+-+-+-+-+-+-+-+ -------------------------------------------------------------------------------------------------------

class Content(NamedTuple):
  header  : Text
  quote   : Text
  content : Any

def content(header : Text, quote : Text, content : Any) -> Content:
  return Content(header, quote, content)

def index_content() -> Content:
  return content(
    greeting(),
    'Pull up some hardware, we\'ve got work to do..',
    pages.get(f'{PAGE_DIR}/index', '')
  )

def blog_content()  -> Content:
  buf = list(filter(lambda x : x.path.startswith(POST_DIR), pages))
  buf.sort(key=lambda x : x['date'], reverse=True)
  return content(
    'The Blog',
    'Views expressed are potentially the authors, please direct any concerns to our complaints department.. Points at trash.',
    buf
  )

def bin_content()   -> Content:
  buf = list(filter(lambda x : x.path.startswith(PROJ_DIR), pages))
  buf.sort(key=lambda x : x['order'])
  return content(
    'Projects',
    'Rifling through the garbage are we? Anything useful.. wget that.',
    buf
  )

def info_content()  -> Content:
  return content(
    'Contacts and About',
    '"At your discretion.."',
    pages.get(f'{PAGE_DIR}/info', ''),
  )

def fetch_post(name : Text) -> Text:
   return pages.get(f'{POST_DIR}/{name}', '')
#--
# -+-+-+-+-+-+-+-+-+-+ -------------------------------------------------------------------------------------------------------
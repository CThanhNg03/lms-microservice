import os
from jinja2 import Environment, FileSystemLoader

current_dir = os.path.dirname(__file__)

templates = Environment(loader=FileSystemLoader(f'{current_dir}/templates'))

invoice_template = templates.get_template('invoice.html')
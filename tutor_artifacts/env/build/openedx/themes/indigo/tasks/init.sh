# Assign themes only if no other theme exists yet
./manage.py lms shell -c "
import sys
from django.contrib.sites.models import Site
def assign_theme(domain):
    site, _ = Site.objects.get_or_create(domain=domain)
    if not site.themes.exists():
        site.themes.create(theme_dir_name='indigo')

assign_theme('lms.biolnks.io')
assign_theme('lms.biolnks.io')
assign_theme('lms.biolnks.io:8000')
assign_theme('cms.biolnks.io')
assign_theme('cms.biolnks.io:8001')
"
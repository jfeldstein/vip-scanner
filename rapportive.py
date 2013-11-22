#!/usr/bin/env python

# rapportive.py
# Author: Jordan <jmwright798@gmail.com>

import sys
import json
import random
import string
import logging
import argparse
import re

# Requests, from python-requests.org
import requests

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
logger = logging.getLogger('rapportive')
logger.setLevel(logging.INFO)

def ___rand_letters(size):
    return ''.join(random.choice(string.ascii_lowercase) for x in range(size))

def request(email, session):
    '''

    rapportive_request(email): Sends a query to the undocumented Rapportive API using a random gmail address
                               Returns the response as a dict
    '''
    profile = {}
    profile = requests.get('https://profiles.rapportive.com/contacts/email/' + email, 
        headers = {'X-Session-Token' : session}).json()
    profile['email'] = email
    return profile

def parse_summary(email, profile):
    '''

    rapportive_summary(profile): Returns a summary of the Rapportive results for an email address
    '''
    summary = ''
    name = ''
    company = ''
    title = ''
    memberships = {'Twitter':'', 'LinkedIn':'', 'AngelList':''}
    if 'contact' in profile and profile['contact']:
        person = profile['contact']
        if 'name' in person and person['name']:
            name = person['name']
        if 'occupations' in person and person['occupations']:
            occupation = person['occupations'][0]
            if 'company' in occupation:
                company = occupation['company']
            if 'job_title' in occupation:
                title = occupation['job_title']
        if 'memberships' in person and person['memberships']:
            for membership in person['memberships']:
                if 'site_name' in membership and membership['site_name']:
                    if 'profile_url' in membership and membership['profile_url']:
                        memberships[membership['site_name']] = membership['profile_url']
        summary = '%s,%s,"%s","%s",%s,%s,%s' % (email, name, company, title, memberships['Twitter'], memberships['AngelList'], memberships['LinkedIn'])
    return summary

def ___process_email(email, session, output_file=None):
    email = email.rstrip()
    profile = request(email, session)
    if 'success' in profile and profile['success'] != 'nothing_useful':
        logger.info('Found match for ' + email)
        summary = parse_summary(email, profile)
        print(summary)
        if output_file:
            output_file.write(summary + '\n')
    else:
         print("No information found\n")

def ___get_session():
    email_addr = ___rand_letters(5) + '@gmail.com'
    logger.info('Using ' + email_addr)
    response = requests.get('https://rapportive.com/login_status?user_email=' + email_addr).json()
    logger.debug('Session token: ' + response['session_token'])
    return response['session_token']

def main():
    '''

    main(): Expect a list of email addresses via stdin and check them with the Rapportive API
            If the --jigsaw flag is set, format the output from the jigsaw.rb tool and check each
            address.
    '''
    parser = argparse.ArgumentParser(description='Check list of emails using Rapportive API')
    parser.add_argument('--output', '-o', type=argparse.FileType('w'), help='Output file to write results to')
    parser.add_argument('--email', '-e', help='Single email address to test')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    session = ___get_session()
    
    if args.email:
        ___process_email(args.email, session, args.output)
    else:
        for line in sys.stdin:
            ___process_email(line, session, args.output)
        
if __name__ == '__main__':  
    main()

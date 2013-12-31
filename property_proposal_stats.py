#!/usr/bin/env python

"""
property_proposals_stats.py: Tabulates and exports statistics for proposed Wikidata properties.

Dependencies:
* Python (2.x)
* Requests (http://docs.python-requests.org/en/latest/)

Instructions:
* Before using this script, first review the KNOWN_TYPES list to ensure that it contains all acceptable data types.
* Then run it from the command-line with "python property_proposals_stats.py".
* Enter input when prompted to clarify ambiguous data type titles.
* The output will be printed to stdout in CSV format.

Created 31 December 2013 by Allen Guo (http://github.com/guoguo12).
This work is in the public domain.
"""

import requests
import collections
import re

# find proposal topics
# download wiki markup of each proposal page
# extract from each proposal the title and type
# count types up, forcing user input on non-standard types
# print data in CSV format

KNOWN_TYPES = ['item', 'string', 'media', 'coordinate', 'monolingual text', 'multilingual text', 'time', 'number', 'url']
clarifications = {}


def get_page(title):
    r = requests.get('https://www.wikidata.org/w/api.php?format=xml&action=query&titles=%s&prop=revisions&rvprop=content' % title)
    return r.content


def get_proposal_topics():
    topics = re.findall('Wikidata:Property proposal/(.*)\|', get_page('Wikidata:Property_proposal'))
    return topics[:-3]  # Ignore 'all', 'Archive', and 'Pending'


def get_proposal_page(topic):
    return get_page('Wikidata:Property_proposal/%s' % topic)


def clarify_type(type):
    while not type.lower() in KNOWN_TYPES:
        print 'clarify type ("skip" to ignore): "%s"' % type
        input = raw_input()
        clarifications[type] = input
        if input.lower() == 'skip':
            return None
        type = input
    return type


def generate_csv(topics, counters):
    print 'Type,Total,' + ','.join(topics)
    for type in KNOWN_TYPES:
        counter = counters[type]
        line = [type, str(counter['all'])]
        for topic in topics:
            if topic in counter:
                line.append(str(counter[topic]))
            else:
                line.append('0')
        if not sum(map(int, line[2:])) == int(line[1]):
            print '<!-- warning: total for following line does not equal sum of parts -->'
        print ','.join(line)


def main():
    counters = {}
    for type in KNOWN_TYPES:
        counters[type] = collections.Counter()
    topics = get_proposal_topics()
    for topic in topics:
        print 'processing topic:', topic
        page = get_proposal_page(topic)
        types = re.findall('\|.*datatype.*=(.*?)[\|\n]', page)
        for type in types:
            type = type.lower().strip()
            if not type in KNOWN_TYPES:
                type = clarify_type(type)
            if type == None:
                continue
            counter = counters[type]
            counter['all'] += 1
            counter[topic] += 1
    print '\nall proposals processed'
    for key, value in clarifications.iteritems():
        if value.lower() == 'skip':
            print 'skipped "%s"' % key
        else:
            print 'clarified "%s" -> "%s"' % (key, value)
    print 'data (in csv format) follows\n'
    generate_csv(topics, counters)


if __name__ == '__main__':
    main()

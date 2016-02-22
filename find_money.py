#!/usr/bin/python

import argparse
import csv
from collections import defaultdict

import re
from selenium import webdriver

browser = webdriver.Firefox()
browser.implicitly_wait(1)


def make_contacts_dict(contacts_file):
    """Convert the contacts file into a dict."""
    with open(contacts_file, 'r', encoding='utf-16') as f:
        return list(csv.DictReader(f))


def get_float_from_string(str):
    """Clear out any junk and get the right value as a float."""
    return float(re.findall("\d+\.\d+", str)[0])


def get_p_type_details(link):
    """Get the details off the detail page for properties held by the state."""
    browser.get(link)
    return {
        'reporter': browser.find_element_by_id('ReportedByData').text,
        'amount': get_float_from_string(browser.find_element_by_id(
                'ctl00_ContentPlaceHolder1_CashReportData'
            ).text),
        'property_type': browser.find_element_by_id('PropertyTypeData').text,
    }


def get_n_or_i_type_details(link):
    """Get the details off the details page for properties held by the
    business.
    """
    browser.get(link)
    return {
        'reporter': browser.find_element_by_id('HolderNameData').text,
        'property_type': browser.find_element_by_id('PropertyTypeData').text,
        'amount': browser.find_element_by_id('AmountData').text,
    }


def get_type_from_image(td):
    """We convert a link to an image of a letter to the actual letter."""
    src = td.find_elements_by_xpath('img')[0].get_attribute('src')
    if 'pIcon' in src:
        return 'p'
    elif 'nIcon' in src:
        return 'n'
    elif 'iIcon' in src:
        return 'i'


def submit_contact(contact, reverse_names=False):
    """Submit the person to the website, return a list of results.

    If reverse_names is True, reverse the first and last names and see if
    results come up that way -- they sometimes do.
    """
    # Submit the name
    browser.get("https://ucpi.sco.ca.gov/ucp/Default.aspx")
    last_name_box = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtLastName')
    first_name_box = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtFirstName')

    # Clear the boxes. Somehow the values are in cookies between page loads.
    last_name_box.clear()
    first_name_box.clear()
    if reverse_names is False:
        # Do it normally
        if not contact['Family Name']:
            return []
        last_name_box.send_keys(contact['Family Name'])
        first_name_box.send_keys('%s\n' % contact['Given Name'])
    else:
        # Reverse first and last names.
        if not contact['Given Name']:
            return []
        last_name_box.send_keys(contact['Given Name'])
        first_name_box.send_keys('%s\n' % contact['Family Name'])

    # Get the table of results
    result_rows = browser.find_elements_by_css_selector(
            '#ctl00_ContentPlaceHolder1_gvResults tr')
    if (result_rows and
                len(result_rows[-2].find_elements_by_xpath('td')) == 1):
        print("WARNING: '{} {}' had a ton of results and was skipped.".format(
            contact['Given Name'],
            contact['Family Name'],
        ))
        return []

    findings = []
    for row in result_rows:
        # Convert each row to a dict
        tds = row.find_elements_by_css_selector('td')
        if tds:
            link = tds[3].find_elements_by_xpath('a')[0].get_attribute('href')
            finding = {
                'email': contact['E-mail 1 - Value'],
                'address1': tds[1].text,
                'address2': tds[2].text,
                'link_id': tds[3].text,
                'type': get_type_from_image(tds[4]),
                'link': link,
                'reverse': reverse_names,
            }
            findings.append(finding)

    # Get the details in a second pass, or else we lose the table of results
    # from Selenium when we go to the next page.
    for finding in findings:
        if finding['type'] == 'p':
            details = get_p_type_details(finding['link'])
        elif finding['type'] in ['n', 'i']:
            details = get_n_or_i_type_details(finding['link'])
        else:
            print("WARNING: Unknown claim type.")
            details = {}
        finding.update(details)

    return findings


def generate_report_data(contacts):
    """Submit each contact to the state website. Return data about the
    results.
    """
    report = defaultdict(list)
    for contact in contacts:
        contact_name = "%s %s" % (
            contact['Given Name'],
            contact['Family Name'],
        )
        report[contact_name].extend(submit_contact(contact))
        report[contact_name].extend(submit_contact(contact, reverse_names=True))
    return report


def print_report(report_data):
    """Print out the findings"""
    for person, findings in report_data.items():
        print("\n{} has {} debts to claim:".format(
            person,
            len(findings),
        ))
        for i, finding in enumerate(findings, 1):
            if finding['type'] == 'p':
                print("  {}. ${} from {} with address {}, {}.".format(
                    i,
                    finding['amount'],
                    finding['reporter'],
                    finding['address1'],
                    finding['address2'],
                ))
                if finding['reverse'] is True:
                    print("    Sneakiness alert! This claim only comes up if "
                          "you reverse {}'s first and last names!".format(
                        person,
                    ))
            elif finding['type'] in ['n', 'i']:
                print('  {}. {} of {} from {} with address {}, {}.'.format(
                    i,
                    finding['amount'],
                    finding['property_type'],
                    ' '.join(finding['reporter'].split()),
                    finding['address1'],
                    finding['address2'],
                ))


def main():
    parser = argparse.ArgumentParser(
        description='Generate a report of how much money your friends can '
                    'claim from the State of California.')
    parser.add_argument(
            '-f', '--contacts-file',
            help='The path to your contacts file.',
            required=True
    )
    args = parser.parse_args()

    contacts = make_contacts_dict(args.contacts_file)
    report_data = generate_report_data(contacts)
    print_report(report_data)
    browser.close()


if __name__ == '__main__':
    main()

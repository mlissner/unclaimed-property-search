# Get Money

A little-known fact is that when somebody owes you money in the state of California, they have to send it to the state for claim. In the words of California's Controller, Betty T. Yee:

> California's Unclaimed Property Law requires corporations, businesses, associations, financial institutions, and insurance companies (referred to as "Holders") to annually report and deliver property to the California State Controller's Office after there has been no activity on the account or contact with the owner for a period of time specified in the law - generally (3) three years or more.

So, you can easily put your name in their search tool, but it's more fun to put your entire contacts list into their search tool and then generate a report or send them an email.

You'll be the belle of the ball when you tell everybody how much money they have to claim.


# Installation

Download the code, then run:

    pip install -r requirements.txt


# Usage

1. Go to Gmail contacts and export your contacts as a Google CSV.

1. Remove anybody the CSV that you don't want to check or just go ahead and check everybody.

1. Run the script on the CSV:

        python find_money --contacts-file your-contacts.csv

1. Email your friends or whatever to tell them they've got cash or property awaiting them. Unfortunately, you can't give them a URL to go to because everything relies on cookies in this website, but if they search their name and find the claim, they can eaisly file a claim online.


# License

MIT. Have fun, folks.

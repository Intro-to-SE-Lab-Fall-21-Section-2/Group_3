This email client uses a web-based user interface,downloads emails via IMAP, stores mail in a SQLite DB, and transmits via SMTP.

Adam Kuhnel - vinnykuhnel Ricardo (Richie) Ledezma - R-Ledezma Johnny Wilson - jw5743 David Patel - davidpatel77

We have decided to use Python along with the Django Web Framework. We are undecided about what services or tools we will use to implement our SMTP and IMAP interfaces.

Users will need the ability to login into their profile and feel that their information is private. The user will be directed to the main page that has drop down box that allows a user to select different email providers and have them enter their credentials. They will need to be able to compose, forward, reply, and attach attachments to their email. They will also need to be able to search through old emails in their inbox as well using a search bar. The objective of the email client is for each function stated above to work properly and allow the user to get throught their tasks.

- This is our test email account to log in for Gmail:

Username: exampleaccgrp3@gmail.com
Password: Group3secret

- This is our test email account to log in for Outlook:

Username: exampleyesgreen@outlook.com
Password: Firefox1234

**In order to for this repo to start working, the user will need to install these components:**
1. You will need to have had "pip" installed on your device already and if not you can use the internet to install "pip"
2. Then install Python3 installed using the command line if has not been installed already
3. Then install Django web framework using the "pip install django" on the command line
4. Then install pyzmail using "pip install pyzmail36" on the command line
5. Then install IMAP client using "pip install imapclient" on the command line

**Now to run the Email Client, the user will need to:**
1. Before running, you must create migrations. Type "python3 manage.py makemigrations" and then "python3 manage.py migrate" into the command line
2. Now to run it, go into the emailClient directory and type "python3 manage.py runserver" into the command line
3. 




from threading import Thread
from time import time
import imap_tools
from imap_tools import MailBox, AND
from datetime import datetime, timedelta
from utils.env import info, FOLDERS, USER_PASSWD_LIST
from utils.return_project_root import get_project_root


def _grab_all_ftl_messages(num_emails_found, _user, _passwd,
                           folder, from_, out, printed, _day, _day_str):
    with MailBox('imap.gmail.com').login(_user, _passwd, initial_folder=folder) \
            as mailbox:
        for msg in mailbox.fetch(
                AND(from_=from_,
                    date=datetime.date(datetime.today() - timedelta(days=_day)),
                    ),
                mark_seen=True,
                bulk=True
        ):
            if not printed:
                info(f'Currently Grabbing {folder} in {_user} from {_day_str}')
                printed = True

            # simple split to grab emails
            string = msg.html.split('"https://www.footlocker.ca/')[1].split('" style="')[0]
            string = f'https://www.footlocker.ca/{string}'
            out.append(string)

            num_emails_found += 1
        if num_emails_found != 0:
            info(f'Done Grabbing {num_emails_found} Emails. {folder} in {_user} from {_day_str}')
        else:
            info(f'No Emails Found. {folder} in {_user} from {_day_str}')


def _grab_ftl_emails(_user, _passwd, _day, out,
                     folders: list = None,
                     from_: str = 'support@e.flxprogram.com',
                     ):
    """
    :param _user: username of the email box
    :param _passwd: username of the email box
    :param _day: day to grab emails from 0 for today, 1 for yesterday, 2 for the day before yesterday, etc
    :param out: the global list all threads write to
    :param folders: the folders we're going to check
    :param from_: the email we expect our verification links to come from
    :return: None, appends to global list of emails.
    """
    _day_str = None
    if _day == 0:
        _day_str = 'Today'
    if _day == 1:
        _day_str = 'Yesterday'
    if not folders:
        folders = FOLDERS
    printed = False
    for folder in folders:
        num_emails_found = 0
        try:
            _grab_all_ftl_messages(num_emails_found, _user, _passwd, folder,
                                   from_, out, printed, _day, _day_str)
        except imap_tools.errors.MailboxFolderSelectError:
            info(f'{folder} not found in {_user}')
            continue


def grab_ftl_emails():
    def _make_old_file():
        # moving everything to `old_emails_to_confirm`
        with open(f'{get_project_root()}/verification_links/emails_to_confirm', 'r') as file:
            new = [line.strip() for line in file.readlines() if len(line) > 10]

        with open(f'{get_project_root()}/verification_links/old_emails_to_confirm', 'r') as file:
            old = [line.strip() for line in file.readlines() if len(line) > 10]

        to_write = new + old
        to_write = list(set(to_write))
        info(f'\n'
             f'\tMost Recently Grabbed List: {len(new)}\n'
             f'\tAll Grabbed: {len(old)}')
        out_str = '\n'.join(to_write)
        with open(f'{get_project_root()}/verification_links/old_emails_to_confirm', 'w') as file:
            file.write(out_str)
        return to_write

    info('Started')
    old_links = set(_make_old_file())
    out = []
    user_passwd_list = USER_PASSWD_LIST
    threads = []
    t1 = time()

    # built this to go over a few days originally
    for day in [0]:
        for user, passwd in user_passwd_list:
            _thread = Thread(target=_grab_ftl_emails, args=(user, passwd, day, out))
            threads.append(_thread)
            _thread.name = user
            _thread.start()
    info(f'{len(threads)} Threads Currently Running')

    # wait for all threads to complete
    for thread in threads:
        thread.join()

    info(f'Grabbed {len(out)} emails.')
    info(f'{len(out)} Before Dedupe')

    # just making sure there are no duplicate links
    out = set(out)
    info(f'{len(out)} After Dedupe')
    out = list(out - old_links)
    info(f'{len(out)} After Filter Old Emails.')

    # turning it into a string and writing it all at once
    out = '\n'.join(out)
    with open(f'{get_project_root()}/verification_links/emails_to_confirm', 'w') as file:
        file.write(out)
    t2 = time()
    info(f'Took {(t2 - t1) / 60:.2f}m')


if __name__ == "__main__":
    grab_ftl_emails()

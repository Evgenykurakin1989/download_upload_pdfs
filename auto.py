import os
import requests
from config import *
import egnyte
from urllib.parse import urlencode
import time
from apscheduler.schedulers.background import BlockingScheduler
from pytz import utc

scheduler = BlockingScheduler()


outdir = "pdfs"
sess = requests.session()

ConnectionID = ""
ConnectionToken = ""

client = egnyte.EgnyteClient({"domain": "ccbfiles.egnyte.com", "access_token": "axdx2jem4rbymyn75anqzt62"})

filenames = []

def get_files_list():
    """
    Get file name list of egnyte
    """
    global filenames
    folder = client.folder("/Shared/OmniSign/pdfs")
    folder.list()
    for file_obj in folder.files:
        filenames.append(file_obj.name)


def login():
    """
    Login with Credentials USER and PASS
    :return: None
    """
    global USER, PASS

    payload = {
        "Login": USER,
        "Password": PASS,
        "Remeber": False
    }

    sess.get("%sLogin" % BASE_URL)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    res = sess.post("%sAjax/Sign/Logon" % BASE_URL, data=payload, headers=headers)

    if res.text == '2':
        dashboard()
    else:
        print("Login failed! Error code is %s" % res.text)


def dashboard():
    """
    Redirect to Dashboard page
    """
    global ConnectionID

    sess.get("%sDashboard" % BASE_URL)
    cookie = sess.cookies.get_dict()

    stagelist = ["132", "216", "338", "252", "365"]
    for stage in stagelist:
        # Get_Ajax
        URL = "%sAjax/Agent/Get_Ajax" % BASE_URL
        payload = {
            "Agents": "",
            "Campaigns": "",
            "ConnectionID": "",
            "Field1": "10065",
            "Field2": "10011",
            "Field3": "18263",
            "Stage": stage,
            "Teams": "",
            "Templates": ""
        }
        sess.post(URL, data=payload)

        # getting connectionID
        URL = "https://hub1.omnisign.co.uk/signalr/negotiate?"
        payload = {
            "clientProtocol": 1.5,
            "connectionData": [{"name": "dashboardhub"}],
            '_': lambda: int(round(time.time() * 1000))
        }

        URL = URL + urlencode(payload)
        res = requests.get(URL).json()
        ConnectionID = res['ConnectionId']

        paperworkdashboard(cookie, stage)


def paperworkdashboard(cookie, stage):
    """
    Redirect to PaperworkDashboard
    """
    global ConnectionID
    URL = "%sAjax/Paperworks/Paperwork_Completed" % BASE_URL

    headers = {
        "Content-Type": "application/json",
        "cookie": "; ".join([str(x) + "=" + str(y) for x, y in cookie.items()])
    }

    payload = {
        "AI": {
            "Agents": "",
            "Templates": "",
            "Teams": "",
            "Campaigns": "",
            "Stage": stage,
            "Field1": "10065",
            "Field2": "10011",
            "Field3": "18263",
            "ConnectionID": ConnectionID,
            "Section": 4
        }
    }


    res = sess.post(URL, json=payload, headers=headers).json()

    processData(res, cookie)


def processData(json_input, cookie):
    """
    Process for download pdf files
    """
    global filenames, outdir

    for item in json_input:
        PackID = item['PackID']
        CodeID = item['CodeID']

        URL = "%sAjax/Paperworks/Paperwork_Completed_Modal" % BASE_URL

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": "; ".join([str(x) + "=" + str(y) for x, y in cookie.items()])
        }

        payload = {
            "PackID": PackID,
            "CodeID": CodeID
        }

        res = sess.post(URL, data=payload, headers=headers).json()

        history = res['History']
        for hist_item in history:
            hist_codeID = hist_item['CodeID']

            filename = "%d.pdf" % hist_codeID
            if filename in filenames:
                continue

            PDF_URL = BASE_URL + "PDF/" + str(hist_codeID)
            headers = {
                "cookie": "; ".join([str(x) + "=" + str(y) for x, y in cookie.items()])
            }

            pdffile = requests.get(PDF_URL, allow_redirects=True, headers=headers)

            filename = os.path.join(outdir, filename)
            with open(filename, "wb") as code:
                code.write(pdffile.content)


def job():
    print("Start working ...")
    if (not os.path.exists(outdir)):
        os.makedirs(outdir)

    # get file name list of already downloaded
    get_files_list()

    # login and start downloading
    try:
        login()
    except Exception as e:
        print(e)
    # after downloading, bulk upload files to ng
    client.bulk_upload([outdir], UPLOAD_DIR)


def schedule_actions():
    global scheduler
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=8, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=9, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=10, minute=43, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=11, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=12, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=13, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=14, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=15, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=16, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=17, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=18, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=19, minute=00, timezone=utc)
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=20, minute=00, timezone=utc)

if __name__ == '__main__':
    print("Automation is starting ...")
	job()
    #schedule_actions()
    #scheduler.start()


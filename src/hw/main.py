import click
import requests
from bs4 import BeautifulSoup
import pickle
import os
from dotenv import dotenv_values

s = requests.Session()

cwd = os.getcwd()
SESS_PKL_F = os.path.join(cwd, '.q2a.session')
config = dotenv_values(os.path.join(cwd, ".env"))


def session_valid():
    if os.path.isfile(SESS_PKL_F):
        with open(SESS_PKL_F, 'rb') as f:
            cookies = pickle.load(f)
        s.cookies.update(cookies)
        r = s.get("https://q2a.di.uniroma1.it/homeworks/visualize")
        if str(config['USERNAME']) in r.text:
            return True


def get_csrf_token(url: str) -> str:
    r = s.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.body.find('input', attrs={'name': 'code'}).get(  # type: ignore
        'value')  # type: ignore


def login():
    if not session_valid():
        url = "https://q2a.di.uniroma1.it/login?to="

        token = get_csrf_token(url)
        data = {"emailhandle": config['USERNAME'],
                "password": config['PASSWORD'],
                "code": token,
                "dologin": "Login"}
        r = s.post(url, data=data)
        if not str(config['USERNAME']) in r.text:
            print("Cant login.")
            exit()
        with open(SESS_PKL_F, "wb") as f:
            pickle.dump(s.cookies, f)

    print("logged in succesfully.")


@click.group()
def cli():
    login()


@cli.command
def eff() -> None:
    r = s.get("https://q2a.di.uniroma1.it/homeworks/visualize")
    soup = BeautifulSoup(r.text, features="html.parser")
    for item in soup.body.find_all('td'):  # type:ignore
        if "Uploaded" in item.text:
            print('Current submission is not checked yet.')
    for item in soup.body.find_all('td'):  # type:ignore
        if "msec" in item.text:
            print("Last Submission Efficiency:", float(
                item.text.replace("msec", "").strip()))
            break


@cli.command
def submit():
    url = f"https://q2a.di.uniroma1.it/homeworks/delivery?homework={config['HOMEWORK_NO']}#form-delivery"
    token = get_csrf_token(url)
    data = {"code": token,
            'homework': config['HOMEWORK_NO'],
            'MAX_FILE_SIZE': '100000',
            'dodelivery': 'Delivery'}
    files = {}
    with open('program01.py', "r") as f:
        files['1source'] = f.read()
    with open('algorithm.txt') as f:
        files['1pseudocode'] = f.read()
    r = s.post(url, data=data, files=files)
    print(r.text)


if __name__ == "__main__":
    cli()
    # if login():
    #     print(find_efficiency())
    # else:
    #     print("login failed")

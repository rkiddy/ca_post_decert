import re

import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from sqlalchemy import create_engine

cfg = dotenv_values(".env")

con_engine = create_engine(f"mysql+pymysql://{cfg['USR']}:{cfg['PWD']}@{cfg['HOST']}/{cfg['DB']}")
conn = con_engine.connect()


def db_exec(engine, sql):
    # print(f"sql: {sql}")
    if sql.strip().startswith('select'):
        return [dict(r) for r in engine.execute(sql).fetchall()]
    else:
        return engine.execute(sql)


def fetch_data(url):
    source_code = requests.get(url).text
    soup = BeautifulSoup(source_code)
    return soup


def fetch_from_file(fn):
    f = open(fn, 'r')
    soup = BeautifulSoup(f.read(), features="html.parser")
    f.close()
    return soup


def clean(txt):
    # print(f"clean:: start txt: {txt}")
    cleaned = ''
    txt2 = txt.replace('&amp;', '&')

    for line in txt2.split('\n'):
        if 'strikethrough text' not in line:
            cleaned += line

    # print(f"clean:: returning: {cleaned}")
    return cleaned.strip().strip(' ')


def untag(txt):

    # print(f"untag:: start txt: {txt}")

    txt2 = txt.replace('<s>', '{s}').replace('</s>', '{/s}')
    tags = list()
    start = None
    for idx in range(len(txt2)):
        if txt2[idx] == '<':
            start = idx
        if txt2[idx] == '>' and start is not None:
            tags.append([start, idx])
            start = None

    # print(f"tags: {tags}")

    txt3 = list(txt2)
    while len(tags) > 0:
        s = tags[-1][0]
        e = tags[-1][1]
        del txt3[s:(e+1)]
        tags.pop()

    txt4 = ''.join(txt3).replace('{', ' <').replace('}', '>')

    # print(f"untag: returning: {txt4}")
    return txt4


def clean_and_untag(txt):
    #return untag(clean(txt))
    return clean(untag(txt))


def sql_fix(txt):
    if txt == '':
        return 'NULL'
    else:
        return f"'{txt.replace("'", "''").replace('%', '%%')}'"


def split_last_employ(txt):
    # print(f"split_last_employ:: start txt: {txt}")
    try:
        idx = txt.index('(')
    except:
        return [txt]

    # we know we have something.
    #
    # no idea why, but there might be a <tab> after the LEA name.
    #
    pre_part = txt[:idx].strip().strip(' ')

    post_part = txt[idx:]

    found = re.search('[0-9]{2}\\/[0-9]{2}\\/[0-9]{4}', post_part)
    if found:
        last_employ_date = found.group(0)
        post_part = post_part[1:found.start()]
    else:
        last_employ_date = None
        post_part = post_part.replace('(', '').replace(')', '')

    post_part = post_part.replace('last employed', '')\
                         .replace('Last employed', '')\
                         .replace('-', '')

    post_part = post_part.strip().strip(' ')

    r = [pre_part]
    if last_employ_date:
        r.append(last_employ_date)
    else:
        r.append('')
    if post_part != '':
        r.append(post_part)

    # print(f"split_last_employ:: returning {r}")
    return r


if __name__ == "__main__":

    # soup = fetch_data('https://post.ca.gov/Peace-Officer-Certification-Actions')
    soup = fetch_from_file('all.txt')

    pk = 1

    for elt in soup.find_all('tr'):

        cells = elt.find_all('td')

        if len(cells) == 7:

            parts = list()
            parts.append(str(pk))
            pk += 1

            last_name = sql_fix(cells[0].text)
            first_name = sql_fix(cells[1].text)
            cert_action = sql_fix(clean_and_untag(str(cells[2])))
            effect_date = sql_fix(clean_and_untag(str(cells[3])))
            pleadings_orders = sql_fix(clean_and_untag(str(cells[4])))

            last_employ = clean_and_untag(str(cells[5]))
            employs = split_last_employ(last_employ)

            if len(employs) < 1 or len(employs) > 3:
                raise Exception(f"something bad in split_last_employ() from '{last_employ}'")

            if len(employs) == 1:
                last_employ = sql_fix(employs[0])
                last_employ_date = 'NULL'
                last_employ_note = 'NULL'

            if len(employs) == 2:
                last_employ = sql_fix(employs[0])
                last_employ_date = sql_fix(employs[1])
                last_employ_note = 'NULL'

            if len(employs) == 3:
                last_employ = sql_fix(employs[0])
                last_employ_date = sql_fix(employs[1])
                last_employ_note = sql_fix(employs[2])

            basis = sql_fix(clean_and_untag(str(cells[6])))

            parts.append(last_name)
            parts.append(first_name)
            parts.append(cert_action)
            parts.append(effect_date)
            parts.append(pleadings_orders)
            parts.append(last_employ)
            parts.append(last_employ_note)
            parts.append(last_employ_date)
            parts.append(basis)

            sql = f"insert into decerts values ({', '.join(parts)})"

            # print(f"\nsql: {sql}")
            db_exec(conn, sql)

    print("")


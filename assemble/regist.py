from .models import URL,URL_BigTag,URL_FineTag,BigTag,FineTag
from django.db import connection

def selecter(url,userid):
    """ selecter 0...スパム 1...投稿者登録 2...新規URL """
    cursor = connection.cursor()
    url = url.strip()
    com = f'''
    select assemble_url.id ,assemble_regist.registered_by_id from assemble_regist 
    join assemble_url 
    on assemble_regist.url_id = assemble_url.id 
    where assemble_regist.registered_by_id = '{userid}'
    and assemble_url.url = '{url}'
    '''
    print(com)
    existUR = cursor.execute(com)
    print("existUR=")
    print(existUR)
    if existUR != 0: #registerがすでにある
        selecter = 0
    else :
        com = f'''
        select id from assemble_url 
        where assemble_url.url = '{url}'
        '''
        existU = cursor.execute(com)
        if existU != 0:
            selecter = 1
        else:
            selecter = 2
    print("selecter="+str(selecter))

    return selecter
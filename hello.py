import os
from flask import Flask, render_template, request, url_for
from pattern.en import tag
import sqlite3dbm
import itertools
import re

app = Flask(__name__)
#app.config['SHELVE_FILENAME'] = 'word_result.shelve'
#init_app(app)
#word_complete =  get_shelve('c')
tag_table = {'adj.':'JJ' , 'det.':'DT' , 'n.':'NN' , 'v.':'VB.*' , 'prep.':'IN'}



def searchfun(lines):
    database = sqlite3dbm.sshelve.open('query_result.db')
    return_list = []
    try:
        for line in database[lines]:
            return_list.append(line)
    except Exception, e:
        pass
    return return_list

def search_tag(pos_tag , content):
    tag_index = content.split(" ").index(pos_tag)
    temp = content.replace(pos_tag , '_')
    result = searchfun(temp)
    return_list = []
    for item in result:
        pos = str(tag(item)[tag_index][1])
        pattern = re.compile(tag_table[pos_tag])
        if pattern.match(pos):
            return_list.append(item)
    return return_list
def re_align(lists):
    database = sqlite3dbm.sshelve.open('query_result.db')
    result = []
    for statments in list(itertools.permutations(lists , len(lists))):
        statment =  " ".join(statments)
        try:
            if database[statment]:
                result.append(database[statment][0])
        except Exception, e:
            pass
    return result

def getkey(result):
    return int(result.split(" ")[-1])

@app.route('/')
@app.route('/data')
def form(name=None):
    if not request.args.get('index'):
        index = '1'
    else:
        index = str(request.args.get('index'))
    if not request.args.get('k'):
        return render_template('test.html',  name='')
    lines = str(request.args.get('k'))
    result = []
    if '?' in lines:
        temp = lines.replace('?','')
        ans = [['False'], ['True']]
        if not searchfun(temp):
            return render_template('test.html',  name=ans[0], query = lines)
        else:
            return render_template('test.html',  name=ans[1], query = lines)
    



    if '|' in lines:
        lists = lines.split(" ")
        or_index = lists.index('|')
        replace_content = lists[or_index - 1]+' | '+lists[or_index + 1]
        temp = lines.replace(replace_content , lists[or_index - 1])
        result.extend(searchfun(temp))
        temp = lines.replace(replace_content , lists[or_index + 1])
        result.extend(searchfun(temp))
        result = sorted(result , key = getkey , reverse=True)
    if '_' in lines:
        result.extend(searchfun(lines))
    if '*' in lines:
        temp = lines.replace('*','_')
        result.extend(searchfun(temp))
        temp = lines.replace('*','_ _')
        result.extend(searchfun(temp))
        temp = lines.replace('*','_ _ _')
        result.extend(searchfun(temp))
        result = sorted(result , key = getkey , reverse=True)
    if 'adj.' in lines:
        result = search_tag('adj.' , lines)
    if 'det.' in lines:
        result = search_tag('det.' , lines)
    if 'n.' in lines:
        result = search_tag('n.' , lines)
    if 'v.' in lines:
        result = search_tag('v.' , lines)
    if 'prep.' in lines:
        result = search_tag('prep.' , lines)
    if 'r.' in lines:
        temp = lines.replace('r. ','')
        lists = temp.split(" ")
        result = re_align(lists)
    size = min(len(result),76)
    if size != 0:
        return render_template('test.html',index=index, name=result, query = lines, size=size)

    database = sqlite3dbm.sshelve.open('query_result.db')
    try:
        result = database[lines]
    except Exception, e:
        result = ["Not Found!!"]
    return render_template('test.html',index=index, name=result, query = lines, size=size)


def word_complete(lines):
    word_complete = sqlite3dbm.sshelve.open('word_result.db')
    try:
        if " " not in lines:
            return word_complete[lines][:10]
        elif " " == lines[-1] and "_" not in lines:
            if not searchfun((lines + "_")):
                return ['Not Found!! 0']
            else:
                return searchfun((lines + "_"))[:10]
        else:
            prefix = " ".join(lines.split(" ")[:-1]) + " _"
            uncomplete = lines.split(" ")[-1]
            if uncomplete == "":
                return ['Not Found!! 0']
            reg = re.compile("^"+uncomplete)
            result = []
            for word in searchfun(prefix):
                if re.search(reg , word.split(" ")[-2]):
                    result.append(word)
            if not result:
                return ['Not Found!! 0']
            else:
                return result
    except Exception, e:
        return ['Not Found!! 0']


@app.route("/ajax_post_test", methods=['POST'])
def ajax_post_test():
    #if request.method == 'POST':
    #    print request.form["name"] + " " + request.form["city"]
    #    return "<p>Hello AJAX " + request.form["name"].upper() + " " + request.form["city"].upper() + " Test.</p>";
    hint_list = ''
    if request.form["value"] == '':
	    return ''
    words = word_complete(request.form["value"])
    for word in words:
        word = ' '.join(word.split(' ')[:-1])
        hint_list += '<li><a href="?index=1&k='+ word +'">'+word+'</a></li>'
    result = '<ul>'+ hint_list + '</ul>'
    return result



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

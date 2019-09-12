#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#======================================================================
#
# kanaquiz.py - 
#
# Created by skywind on 2019/09/11
# Last Modified: 2019/09/11 16:35:48
#
#======================================================================
from __future__ import unicode_literals, print_function
import sys
import time
import os
import codecs
import json
import random


#----------------------------------------------------------------------
# kana chart
#----------------------------------------------------------------------
KANAS = [
        ('あ', 'ア', 'a', 0, 0),
        ('い', 'イ', 'i', 0, 1),
        ('う', 'ウ', 'u', 0, 2),
        ('え', 'エ', 'e', 0, 3),
        ('お', 'オ', 'o', 0, 4),

        ('か', 'カ', 'ka', 1, 0),
        ('き', 'キ', 'ki', 1, 1),
        ('く', 'ク', 'ku', 1, 2),
        ('け', 'ケ', 'ke', 1, 3),
        ('こ', 'コ', 'ko', 1, 4),

        ('さ', 'サ', 'sa', 2, 0),
        ('し', 'シ', 'shi', 2, 1),
        ('す', 'ス', 'su', 2, 2),
        ('せ', 'セ', 'se', 2, 3),
        ('そ', 'ソ', 'so', 2, 4),

        ('た', 'タ', 'ta', 3, 0),
        ('ち', 'チ', 'chi', 3, 1),
        ('つ', 'ツ', 'tsu', 3, 2),
        ('て', 'テ', 'te', 3, 3),
        ('と', 'ト', 'to', 3, 4),

        ('な', 'ナ', 'na', 4, 0),
        ('に', 'ニ', 'ni', 4, 1),
        ('ぬ', 'ヌ', 'nu', 4, 2),
        ('ね', 'ネ', 'ne', 4, 3),
        ('の', 'ノ', 'no', 4, 4),

        ('は', 'ハ', 'ha', 5, 0),
        ('ひ', 'ヒ', 'hi', 5, 1),
        ('ふ', 'フ', 'fu', 5, 2),
        ('へ', 'ヘ', 'he', 5, 3),
        ('ほ', 'ホ', 'ho', 5, 4),

        ('ま', 'マ', 'ma', 6, 0),
        ('み', 'ミ', 'mi', 6, 1),
        ('む', 'ム', 'mu', 6, 2),
        ('め', 'メ', 'me', 6, 3),
        ('も', 'モ', 'mo', 6, 4),

        ('や', 'ヤ', 'ya', 7, 0),
        ('ゆ', 'ユ', 'yu', 7, 2),
        ('よ', 'ヨ', 'yo', 7, 4),

        ('ら', 'ラ', 'ra', 8, 0),
        ('り', 'リ', 'ri', 8, 1),
        ('る', 'ル', 'ru', 8, 2),
        ('れ', 'レ', 're', 8, 3),
        ('ろ', 'ロ', 'ro', 8, 4),

        ('わ', 'ワ', 'wa', 9, 0),
        ('を', 'ヲ', 'wo', 9, 4),

        ('ん', 'ン', 'n', 10, 0),
    ]


#----------------------------------------------------------------------
# dakuons
#----------------------------------------------------------------------
DAKUON = [
        ('が', 'ガ', 'ga', 0, 0),
        ('ぎ', 'ギ', 'gi', 0, 1),
        ('ぐ', 'グ', 'gu', 0, 2),
        ('げ', 'ゲ', 'ge', 0, 3),
        ('ご', 'ゴ', 'go', 0, 4),

        ('ざ', 'ザ', 'za', 1, 0),
        ('じ', 'ジ', 'ji', 1, 1),
        ('ず', 'ズ', 'zu', 1, 2),
        ('ぜ', 'ゼ', 'ze', 1, 3),
        ('ぞ', 'ゾ', 'zo', 1, 4),

        ('だ', 'ダ', 'da', 2, 0),
        ('ぢ', 'ヂ', 'ji', 2, 1),
        ('づ', 'ヅ', 'zu', 2, 2),
        ('で', 'デ', 'de', 2, 3),
        ('ど', 'ド', 'do', 2, 4),

        ('ば', 'バ', 'ba', 3, 0),
        ('び', 'ビ', 'bi', 3, 1),
        ('ぶ', 'ブ', 'bu', 3, 2),
        ('べ', 'ベ', 'be', 3, 3),
        ('ぼ', 'ボ', 'bo', 3, 4),

        ('ぱ', 'パ', 'pa', 4, 0),
        ('ぴ', 'ピ', 'pi', 4, 1),
        ('ぷ', 'プ', 'pu', 4, 2),
        ('ぺ', 'ペ', 'pe', 4, 3),
        ('ぽ', 'ポ', 'po', 4, 4),
    ]


#----------------------------------------------------------------------
# hiragana/katakana -> romaji
#----------------------------------------------------------------------
ROMAJI = {}

for item in KANAS + DAKUON:
    hiragana, katakana, romaji = item[:3]
    ROMAJI[hiragana] = romaji
    ROMAJI[katakana] = romaji


#----------------------------------------------------------------------
# wcwidth
#----------------------------------------------------------------------
try:
    import wcwidth
    def displaylen(text):
        return wcwidth.wcswidth(text)
except ImportError:
    def displaylen(text):
        return sum([ ((c in ROMAJI) and 2 or 1) for c in text ])


#----------------------------------------------------------------------
# config
#----------------------------------------------------------------------
class configure (object):

    def __init__ (self):
        self.dirhome = os.path.expanduser('~/.cache/kanaquiz')
        if not os.path.exists(self.dirhome):
            self.mkdir(self.dirhome)
        self.config = {}
        self.limit = 10
        self.enable_stdout = True
        self.string_buffer = None
        self.cfgname = os.path.join(self.dirhome, 'quiz.tbl')
        self.load()

    def mkdir (self, path):
        unix = sys.platform[:3] != 'win' and True or False
        path = os.path.abspath(path)
        if os.path.exists(path):
            return False
        name = ''
        part = os.path.abspath(path).replace('\\', '/').split('/')
        if unix:
            name = '/'
        if (not unix) and (path[1:2] == ':'):
            part[0] += '/'
        for n in part:
            name = os.path.abspath(os.path.join(name, n))
            if not os.path.exists(name):
                os.mkdir(name)
        return True

    def load (self):
        self.config = {}
        for item in KANAS + DAKUON:
            h, k = item[:2]
            self.config[h] = []
            self.config[k] = []
        self.config['h'] = []
        self.config['k'] = []
        self.config['a'] = []
        self.config['t'] = []
        config = None
        try:
            with codecs.open(self.cfgname, 'r', encoding = 'utf-8') as fp:
                config = json.load(fp)
        except:
            pass
        if not config:
            return False
        if isinstance(config, dict):
            for k in config:
                v = config[k]
                if k in self.config:
                    self.config[k] = v
        return True

    def save (self):
        with codecs.open(self.cfgname, 'w', encoding = 'utf-8') as fp:
            json.dump(self.config, fp, indent = 4)
        return True

    # set terminal color
    def console (self, color):
        if sys.platform[:3] == 'win':
            import ctypes
            kernel32 = ctypes.windll.LoadLibrary('kernel32.dll')
            GetStdHandle = kernel32.GetStdHandle
            SetConsoleTextAttribute = kernel32.SetConsoleTextAttribute
            GetStdHandle.argtypes = [ ctypes.c_uint32 ]
            GetStdHandle.restype = ctypes.c_size_t
            SetConsoleTextAttribute.argtypes = [ ctypes.c_size_t, ctypes.c_uint16 ]
            SetConsoleTextAttribute.restype = ctypes.c_long
            handle = GetStdHandle(0xfffffff5)
            if color < 0: color = 7
            result = 0
            if (color & 1): result |= 4
            if (color & 2): result |= 2
            if (color & 4): result |= 1
            if (color & 8): result |= 8
            if (color & 16): result |= 64
            if (color & 32): result |= 32
            if (color & 64): result |= 16
            if (color & 128): result |= 128
            SetConsoleTextAttribute(handle, result)
        else:
            if color >= 0:
                foreground = color & 7
                background = (color >> 4) & 7
                bold = color & 8
                sys.stdout.write(" \033[%s3%d;4%dm"%(bold and "01;" or "", foreground, background))
                sys.stdout.flush()
            else:
                sys.stdout.write(" \033[0m")
                sys.stdout.flush()
        return 0

    # echo text
    def echo (self, color, text):
        if self.enable_stdout:
            self.console(color)
            sys.stdout.write(text)
            sys.stdout.flush()
        if self.string_buffer:
            self.string_buffer.write(text)
        return 0

    # new record
    def update (self, kana, elapse):
        if kana not in self.config:
            return False
        self.config[kana].append(elapse)
        if len(self.config[kana]) > self.limit:
            self.config[kana] = self.config[kana][-self.limit:]
        return True

    # average score
    def average (self, kana):
        times = self.config.get(kana)
        times = filter(lambda x: x is not None, times and times or [])
        if not times:
            return None
        return float(sum(times)) / len(times)

    # best score
    def best (self, kana):
        times = self.config.get(kana)
        times = filter(lambda x: x is not None, times and times or [])
        if not times:
            return None
        return min(times)

    # cell display
    def cell_echo (self, rows, row, col, csize):
        if row >= len(rows):
            self.echo(-1, ' ' * (space + 2))
            return 0
        if col >= len(rows[row]):
            output = ' ' * (space + 2)
            self.echo(-1, ' ' * (space + 2))
            return 0
        color, text, align = rows[row][col]
        padding = 2 + csize - displaylen(text)
        if align in ('r', 'right'):
            pad2 = 1
            pad1 = padding - pad1
        elif align in ('c', 'center'):
            pad1 = padding // 2
            pad2 = padding - pad1
        else:
            pad1 = 1
            pad2 = padding - pad1
        self.echo(-1, ' ' * pad1) 
        self.echo(color, text)
        self.echo(-1, ' ' * pad2)
        return 1

    # color table
    def color_table (self, rows, style = 0):
        saverows = rows
        rows = []
        colsize = {}
        maxcol = 0
        if not saverows:
            return False
        for row in saverows:
            newrow = []
            for item in row:
                if isinstance(item, str):
                    ni = (-1, item, None)
                elif isinstance(item, int):
                    ni = (-1, str(item), None)
                elif isinstance(item, float):
                    ni = (-1, str(item), None)
                elif isinstance(item, list) or isinstance(item, tuple):
                    if len(item) == 0:
                        item = (-1, '', None)
                    elif len(item) < 3:
                        item = tuple((list(item) + ['', ''])[:3])
                    ni = (item[0], str(item[1]), item[2].lower())
                newrow.append(ni)
            rows.append(newrow)
        for row in rows:
            maxcol = max(len(row), maxcol)
            for col, item in enumerate(row):
                text = str(item[1])
                size = displaylen(text)
                if col not in colsize:
                    colsize[col] = size
                else:
                    colsize[col] = max(size, colsize[col])
        if maxcol <= 0:
            return False
        if style == 0:
            for j in range(len(rows)):
                for i in range(maxcol):
                    self.cell_echo(rows, j, i, colsize[i])
                self.echo(-1, '\n')
        elif style == 1:
            if rows:
                newrows = rows[:1]
                head = [ '-' * colsize[i] for i in range(maxcol) ]
                newrows.append([ (-1, n, None) for n in head ])
                newrows.extend(rows[1:])
                rows = newrows
            for j in range(len(rows)):
                for i in range(maxcol):
                    self.cell_echo(rows, j, i, colsize[i])
                self.echo(-1, '\n')
        else:
            sep = '+'.join([ '-' * (colsize[x] + 2) for x in range(maxcol) ])
            sep = '+' + sep + '+'
            for y, row in enumerate(rows):
                self.echo(-1, sep + '\n')
                for x in range(maxcol):
                    self.echo(-1, '|')
                    self.cell_echo(rows, y, x, colsize[x])
                self.echo(-1, '|\n')
            self.echo(-1, sep + '\n')
        return True

    # tabulify table
    def tabulify (self, rows, style = 0):
        old_stdout = self.enable_stdout
        old_string = self.string_buffer
        import io
        self.enable_stdout = False
        self.string_buffer = io.StringIO()
        self.color_table(rows, style)
        output = self.string_buffer.getvalue()
        self.enable_stdout = old_stdout
        self.enable_string = old_string
        return output



#----------------------------------------------------------------------
# quizcore
#----------------------------------------------------------------------
class quizcore (object):

    def __init__ (self):
        self.config = configure()
        self.tokens = [] 

    def disorder (self, array):
        array = [ n for n in array ]
        output = []
        while array:
            size = len(array)
            pos = random.randint(0, size - 1)
            output.append(array[pos])
            array[pos] = array[size - 1]
            array.pop()
        return output

    def select (self, source):
        tokens = []
        if not source:
            source = []
        if isinstance(source, str):
            parts = source.split(',')
            source = []
            for n in parts:
                n = n.strip()
                if n: source.append(n)
        check = {}
        for n in source:
            check[n.lower().strip()] = 1
        if 'all' in check:
            check['hiragana'] = 1
            check['katakana'] = 1
        if 'dakuon-all' in check or 'dakuon' in check:
            check['dakuon-hiragana'] = 1
            check['dakuon-katakana'] = 1
        for item in KANAS:
            if 'hiragana' in check:
                tokens.append(item[0])
            if 'katakana' in check:
                tokens.append(item[1])
        for item in DAKUON:
            if 'dakuon-hiragana' in check:
                tokens.append(item[0])
            if 'dakuon-katakana' in check:
                tokens.append(item[1])
        return tokens

    def trinity (self, source):
        tokens = self.select(source)
        tokens = self.disorder(tokens)
        target = [ n for n in tokens ]
        trinity = []
        if not tokens:
            return []
        size = len(tokens)
        for i in range((size + 2) // 3):
            k1 = tokens[random.randint(0, size - 1)]
            k2 = tokens[random.randint(0, size - 1)]
            k3 = tokens[random.randint(0, size - 1)]
            if target:
                k1 = target.pop()
            if target:
                k2 = target.pop()
            if target:
                k3 = target.pop()
            trinity.append(k1 + k2 + k3)
        return trinity

    def echo (self, color, text):
        return self.config.echo(color, text)

    def single_quiz (self, word, heading = ''):
        romans = ''.join([ ROMAJI[c] for c in word ])
        self.config.console(-1)
        self.echo(7, '[')
        self.echo(14, word)
        self.echo(7, ']')
        if heading:
            self.echo(8, ' ' + heading)
        self.echo(-1, '\n')
        answer = None
        ts = time.time()
        while 1:
            self.echo(7, '? ')
            if sys.version_info[0] < 3:
                answer = raw_input()
            else:
                answer = input()
            answer = answer.strip()
            if answer:
                break
        ts = time.time() - ts
        if answer == romans:
            self.echo(2, 'correct')
            self.echo(8, ' (time %.2f)\n'%ts)
            hr = ts
        else:
            self.echo(1, 'wrong')
            self.echo(8, ' (%s->%s)\n'%(answer, romans))
            hr = None
        self.echo(-1, '\n')
        return hr

    def normalize (self, name):
        name = name.lower().strip()
        if name in ('h', 'hiragana'):
            return 'hiragana'
        elif name in ('k', 'katakana'):
            return 'katakana'
        elif name in ('a', 'all'):
            return 'all'
        elif name in ('d', 'dakuon'):
            return 'dakuon'
        elif name in ('t', 'trinity'):
            return 'trinity'
        return ''

    def start (self, name):
        name = self.normalize(name)
        if not name:
            return None
        if name == 'trinity':
            tokens = self.trinity(name)
        else:
            tokens = self.select(name)
        tests = self.disorder(tokens)
        times = {}
        for k in tests:
            times[k] = None
        for i in range(len(tests)):
            word = tests[i]
            head = '(%d/%d)'%(i + 1, len(tests))
            elapse = self.single_quiz(word, head)
            times[word] = head
        return times

    def list_kana (self, mode, romaji):
        rows = []
        source = KANAS
        if mode in ('d', 'dakuon'):
            source = DAKUON
        table = {}
        for item in source:
            y = item[3]
            if y not in table:
                table[y] = []
            table[y].append(item)
        nrows = len(table)
        for j in range(nrows):
            row = ['', '', '', '', '']
            rom = ['', '', '', '', '']
            for item in table[j]:
                pos = item[4]
                eng = item[2]
                row[pos] = (7, item[0] + ' ' + item[1], 'c')
                rom[pos] = (8, eng, 'c')
            rows.append(row)
            if romaji:
                rows.append(rom)
        title = [ (' ' + c) for c in 'あいうえお' ]
        self.config.color_table(rows, 0)
        return True


#----------------------------------------------------------------------
# entry
#----------------------------------------------------------------------
if __name__ == '__main__':
    def test1():
        cfg = configure()
        # cfg.config['a'] = [1,2,3]
        cfg.save()
        print(cfg.config)
        return 0
    def test2():
        quiz = kquiz()
        token = quiz.trinity('all')
        import pprint
        pprint.pprint(token)
        print(len(token), len(KANAS))
        return 0
    def test3():
        quiz = quizcore()
        print(quiz.single_quiz('ただいま', '(1/100)'))
    def test4():
        quiz = quizcore()
        quiz.start('hiragana')
    def test5():
        quiz = quizcore()
        quiz.list_kana('', 0)
    test5()



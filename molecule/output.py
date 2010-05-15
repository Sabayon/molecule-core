#!/usr/bin/python -O
# -*- coding: iso-8859-1 -*-
#    Molecule Disc Image builder for Sabayon Linux
#    Copyright (C) 2009 Fabio Erculiani
#
#    Copyright 1998-2004 Gentoo Foundation
#    # $Id: output.py 4906 2006-11-01 23:55:29Z zmedico $
#    Copyright (C) 2007-2008 Fabio Erculiani
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from molecule.i18n import _
import sys, os
import curses
stuff = {}
stuff['cols'] = 30
try:
    curses.setupterm()
    stuff['cols'] = curses.tigetnum('cols')
except:
    pass
stuff['cleanline'] = ""
def setcols():
    stuff['cleanline'] = ""
    count = stuff['cols']
    while count:
        stuff['cleanline'] += ' '
        count -= 1
setcols()
stuff['cursor'] = False
stuff['ESC'] = chr(27)

havecolor=1
global dotitles
dotitles=1

esc_seq = "\x1b["

g_attr = {}
g_attr["normal"]       =  0

g_attr["bold"]         =  1
g_attr["faint"]        =  2
g_attr["standout"]     =  3
g_attr["underline"]    =  4
g_attr["blink"]        =  5
g_attr["overline"]     =  6  # Why is overline actually useful?
g_attr["reverse"]      =  7
g_attr["invisible"]    =  8

g_attr["no-attr"]      = 22
g_attr["no-standout"]  = 23
g_attr["no-underline"] = 24
g_attr["no-blink"]     = 25
g_attr["no-overline"]  = 26
g_attr["no-reverse"]   = 27
# 28 isn't defined?
# 29 isn't defined?
g_attr["black"]        = 30
g_attr["red"]          = 31
g_attr["green"]        = 32
g_attr["yellow"]       = 33
g_attr["blue"]         = 34
g_attr["magenta"]      = 35
g_attr["cyan"]         = 36
g_attr["white"]        = 37
# 38 isn't defined?
g_attr["default"]      = 39
g_attr["bg_black"]     = 40
g_attr["bg_red"]       = 41
g_attr["bg_green"]     = 42
g_attr["bg_yellow"]    = 43
g_attr["bg_blue"]      = 44
g_attr["bg_magenta"]   = 45
g_attr["bg_cyan"]      = 46
g_attr["bg_white"]     = 47
g_attr["bg_default"]   = 49


def color(fg, bg="default", attr=["normal"]):
        mystr = esc_seq[:] + "%02d" % g_attr[fg]
        for x in [bg]+attr:
                mystr += ";%02d" % g_attr[x]
        return mystr+"m"



codes={}
codes["reset"]     = esc_seq + "39;49;00m"

codes["bold"]      = esc_seq + "01m"
codes["faint"]     = esc_seq + "02m"
codes["standout"]  = esc_seq + "03m"
codes["underline"] = esc_seq + "04m"
codes["blink"]     = esc_seq + "05m"
codes["overline"]  = esc_seq + "06m"  # Who made this up? Seriously.

ansi_color_codes = []
for x in xrange(30, 38):
        ansi_color_codes.append("%im" % x)
        ansi_color_codes.append("%i;01m" % x)

rgb_ansi_colors = ['0x000000', '0x555555', '0xAA0000', '0xFF5555', '0x00AA00',
        '0x55FF55', '0xAA5500', '0xFFFF55', '0x0000AA', '0x5555FF', '0xAA00AA',
        '0xFF55FF', '0x00AAAA', '0x55FFFF', '0xAAAAAA', '0xFFFFFF']

for x in xrange(len(rgb_ansi_colors)):
        codes[rgb_ansi_colors[x]] = esc_seq + ansi_color_codes[x]

del x

codes["black"]     = codes["0x000000"]
codes["darkgray"]  = codes["0x555555"]

codes["red"]       = codes["0xFF5555"]
codes["darkred"]   = codes["0xAA0000"]

codes["green"]     = codes["0x55FF55"]
codes["darkgreen"] = codes["0x00AA00"]

codes["yellow"]    = codes["0xFFFF55"]
codes["brown"]     = codes["0xAA5500"]

codes["blue"]      = codes["0x5555FF"]
codes["darkblue"]  = codes["0x0000AA"]

codes["fuchsia"]   = codes["0xFF55FF"]
codes["purple"]    = codes["0xAA00AA"]

codes["turquoise"] = codes["0x55FFFF"]
codes["teal"]      = codes["0x00AAAA"]

codes["white"]     = codes["0xFFFFFF"]
codes["lightgray"] = codes["0xAAAAAA"]

codes["darkteal"]   = codes["turquoise"]
codes["darkyellow"] = codes["brown"]
codes["fuscia"]     = codes["fuchsia"]
codes["white"]      = codes["bold"]

# Colors from /sbin/functions.sh
codes["GOOD"]       = codes["green"]
codes["WARN"]       = codes["yellow"]
codes["BAD"]        = codes["red"]
codes["HILITE"]     = codes["teal"]
codes["BRACKET"]    = codes["blue"]

# Portage functions
codes["INFORM"] = codes["darkgreen"]
codes["UNMERGE_WARN"] = codes["red"]
codes["MERGE_LIST_PROGRESS"] = codes["yellow"]

def is_stdout_a_tty():
    """
    Return whether current stdout is a TTY.

    @return: tty? => True
    @rtype: bool
    """
    fn = sys.stdout.fileno()
    return os.isatty(fn)

def xterm_title(mystr, raw = False):
    """
    Set new xterm title.

    @param mystr: new xterm title
    @type mystr: string
    @keyword raw: write title in raw mode
    @type raw: bool
    """
    if dotitles and "TERM" in os.environ and sys.stderr.isatty():
        myt = os.environ["TERM"]
        legal_terms = ("xterm", "Eterm", "aterm", "rxvt", "screen",
            "kterm", "rxvt-unicode", "gnome")
        if myt in legal_terms:
            if not raw:
                mystr = "\x1b]0;%s\x07" % mystr
            try:
                sys.stderr.write(mystr)
            except UnicodeEncodeError:
                sys.stderr.write(mystr.encode('utf-8'))
            sys.stderr.flush()

default_xterm_title = None

def xterm_title_reset():
    """
    Reset xterm title to default.
    """
    global default_xterm_title
    if default_xterm_title is None:
        prompt_command = os.getenv('PROMPT_COMMAND')
        if not prompt_command:
            default_xterm_title = ""
        elif prompt_command is not None:
            from entropy.tools import getstatusoutput
            default_xterm_title = getstatusoutput(prompt_command)[1]
        else:
            pwd = os.getenv('PWD', '')
            home = os.getenv('HOME', '')
            if home != '' and pwd.startswith(home):
                pwd = '~' + pwd[len(home):]
            default_xterm_title = '\x1b]0;%s@%s:%s\x07' % (
                os.getenv('LOGNAME', ''),
                os.getenv('HOSTNAME', '').split('.', 1)[0],
                pwd)
    xterm_title(default_xterm_title)

def notitles():
    """
    Turn off title setting. In this way, xterm title won't be touched.
    """
    global dotitles
    dotitles=0

def nocolor():
    """
    Turn off colorization process-wide.
    """
    os.environ['ETP_NO_COLOR'] = "1"
    global havecolor
    havecolor=0
if not is_stdout_a_tty():
    nocolor()

def getcolor():
    """
    Return color status
    """
    return havecolor

nc = os.getenv("ETP_NO_COLOR")
if nc:
    nocolor()

def _reset_color():
    """
    Reset terminal color currently set.
    """
    return codes["reset"]

def colorize(color_key, text):
    global havecolor
    if havecolor:
        return codes[color_key] + text + codes["reset"]
    return text

def decolorize(text):
    my_esc_seq = "\x1b"
    new_text = ''
    append = True
    for char in text:
        if char == my_esc_seq:
            append = False
            continue
        elif char == "m" and not append:
            append = True
            continue
        if append:
            new_text += char
    return new_text

def bold(text):
    """
    Make text bold using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("bold", text)

def white(text):
    """
    Make text white using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("white", text)

def teal(text):
    """
    Make text teal using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("teal", text)

def turquoise(text):
    """
    Make text turquoise using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("turquoise", text)

def darkteal(text):
    """
    Make text darkteal using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("darkteal", text)

def purple(text):
    """
    Make text purple using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("purple", text)

def blue(text):
    """
    Make text blue using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("blue", text)

def darkblue(text):
    """
    Make text darkblue using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("darkblue", text)

def green(text):
    """
    Make text green using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("green", text)

def darkgreen(text):
    """
    Make text darkgreen using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("darkgreen", text)

def yellow(text):
    """
    Make text yellow using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("yellow", text)

def brown(text):
    """
    Make text brown using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("brown", text)

def darkyellow(text):
    """
    Make text darkyellow using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("darkyellow", text)

def red(text):
    """
    Make text red using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("red", text)

def darkred(text):
    """
    Make text darkred using bash/terminal codes.

    @param text: text to colorize
    @type text: string
    @return: colorized text
    @rtype: string
    """
    return colorize("darkred", text)

def print_menu(data, args = None):
    """
    Function used by Entropy text client (will be moved from here) to
    print the menu output given a properly formatted list.
    This method is not intended for general used and will be moved away from
    here.
    """
    if args == None:
        args = []

    def orig_myfunc(x):
        return x
    def orig_myfunc_desc(x):
        return x

    try:
        i = args.index("--help")
        del args[i]
        command = args.pop(0)
    except ValueError:
        command = None
    except IndexError:
        command = None
    section_found = False
    search_depth = 1


    for item in data:
        myfunc = orig_myfunc
        myfunc_desc = orig_myfunc_desc

        if not item:
            if command is None:
                writechar("\n")
        else:
            n_indent = item[0]
            name = item[1]
            n_d_ident = item[2]
            desc = item[3]
            if command is not None:
                name_strip = name.split()[0].strip()
                if name_strip == command and n_indent == search_depth:
                    try:
                        command = args.pop(0)
                        search_depth = n_indent + 1
                    except IndexError:
                        command = "##unused_from_now_on"
                        section_found = True
                        indent_level = n_indent
                elif section_found:
                    if n_indent <= indent_level:
                        return
                else:
                    continue

            if n_indent == 0:
                writechar("  ")
            # setup identation
            ind_th = 0
            if command is not None: # so that partial --help looks nicer
                ind_th = 1
            while n_indent > ind_th:
                n_indent -= 1
                writechar("\t")
            n_indent = item[0]

            # write name
            if n_indent == 0:
                myfunc = darkgreen
            elif n_indent == 1:
                myfunc = blue
                myfunc_desc = darkgreen
            elif n_indent == 2:
                if not name.startswith("--"):
                    myfunc = red
                myfunc_desc = brown
            elif n_indent == 3:
                myfunc = darkblue
                myfunc_desc = purple
            func_out = myfunc(name)
            print_generic(func_out, end = "")

            # write desc
            if desc:
                while n_d_ident > 0:
                    n_d_ident -= 1
                    writechar("\t")
                desc = myfunc_desc(desc)
                print_generic(desc, end = "")
            writechar("\n")

def reset_cursor():
    """
    Print to stdout the terminal code to push back cursor at the beginning
    of the line.
    """
    if havecolor:
        sys.stdout.write(stuff['ESC'] + '[2K')
    _flush_stdouterr()

def _flush_stdouterr():
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except IOError:
        return

def _stdout_write(msg):
    if not isinstance(msg, basestring):
        msg = repr(msg)
    try:
        sys.stdout.write(msg)
    except UnicodeEncodeError:
        msg = msg.encode('utf-8')
        if sys.hexversion >= 0x3000000:
            sys.stdout.buffer.write(msg)
        else:
            sys.stdout.write(msg)

def _print_prio(msg, color_func, back = False, flush = True, end = '\n'):
    if not back:
        setcols()
    reset_cursor()
    is_tty = is_stdout_a_tty()
    if is_tty:
        writechar("\r")
    if back:
        msg = color_func(">>") + " " + msg
    else:
        msg = color_func(">>") + " " + msg + end

    _stdout_write(msg)
    if back and (not is_tty):
        # in this way files are properly written
        writechar("\n")
    if flush:
        _flush_stdouterr()

def print_error(msg, back = False, flush = True, end = '\n'):
    """
    Service function used by Entropy text client (will be moved from here)
    to write error messages to stdout (not stderr, atm).
    NOTE: don't use this directly but rather subclass TextInterface class.

    @param msg: text message to print
    @type msg: string
    @keyword back: move text cursor back to the beginning of the line
    @type back: bool
    @keyword flush: flush stdout and stderr
    @type flush: bool
    @return: None
    @rtype: None
    """
    return _print_prio(msg, darkred, back = back, flush = flush, end = end)

def print_info(msg, back = False, flush = True, end = '\n'):
    """
    Service function used by Entropy text client (will be moved from here)
    to write info messages to stdout (not stderr, atm).
    NOTE: don't use this directly but rather subclass TextInterface class.

    @param msg: text message to print
    @type msg: string
    @keyword back: move text cursor back to the beginning of the line
    @type back: bool
    @keyword flush: flush stdout and stderr
    @type flush: bool
    @return: None
    @rtype: None
    """
    return _print_prio(msg, darkgreen, back = back, flush = flush, end = end)

def print_warning(msg, back = False, flush = True, end = '\n'):
    """
    Service function used by Entropy text client (will be moved from here)
    to write warning messages to stdout (not stderr, atm).
    NOTE: don't use this directly but rather subclass TextInterface class.

    @param msg: text message to print
    @type msg: string
    @keyword back: move text cursor back to the beginning of the line
    @type back: bool
    @keyword flush: flush stdout and stderr
    @type flush: bool
    @return: None
    @rtype: None
    """
    return _print_prio(msg, brown, back = back, flush = flush, end = end)

def print_generic(*args, **kwargs):
    """
    Service function used by Entropy text client (will be moved from here)
    to write generic messages to stdout (not stderr, atm).
    NOTE: don't use this directly but rather subclass TextInterface class.
    """
    # disabled, because it causes quite a mess when writing to files
    # writechar("\r")
    for msg in args:
        _stdout_write(msg)
        sys.stdout.write(" ")

    end = kwargs.get('end', '\n')
    _stdout_write(end)
    _flush_stdouterr()

def writechar(char):
    try:
        sys.stdout.write(char)
        sys.stdout.flush()
    except IOError, e:
        if e.errno == 32:
            return
        raise

def readtext(request, password = False):
    """
    Read text from stdin and return it (will be moved from here).

    @param request: textual request to print
    @type request: string
    @keyword password: if you are requesting a password, set this to True
    @type password: bool
    @return: text read back from stdin
    @rtype: string
    """
    xterm_title(_("Molecule needs your attention"))
    if password:
        from getpass import getpass
        try:
            text = getpass(request+" ")
        except UnicodeEncodeError:
            text = getpass(request.encode('utf-8')+" ")
    else:
        try:
            sys.stdout.write(request)
        except UnicodeEncodeError:
            sys.stdout.write(request.encode('utf-8'))
        _flush_stdouterr()
        text = _my_raw_input()
    return text

def _my_raw_input(txt = ''):
    if txt:
        try:
            sys.stdout.write(darkgreen(txt))
        except UnicodeEncodeError:
            sys.stdout.write(darkgreen(txt.encode('utf-8')))
    _flush_stdouterr()
    response = ''
    while True:
        y = sys.stdin.read(1)
        if y in ('\n', '\r',):
            break
        response += y
        _flush_stdouterr()
    return response

class Output:

    """
    TextInterface is a base class for handling the communication between
    user and Entropy-based applications.

    This class works for text-based applications, it must be inherited
    from subclasses and its methods reimplemented to make Entropy working
    on situations where a terminal is not used as UI (Graphical applications,
    web-based interfaces, remote interfaces, etc).

    """

    def output(self, text, header = "", footer = "", back = False, importance = 0, type = "info", count = None, percent = False):

        _flush_stdouterr()

        myfunc = print_info
        if type == "warning":
            myfunc = print_warning
        elif type == "error":
            myfunc = print_error

        count_str = ""
        if count:
            if len(count) > 1:
                if percent:
                    percent_str = str(round((float(count[0])/count[1])*100, 1))
                    count_str = " ("+percent_str+"%) "
                else:
                    count_str = " (%s/%s) " % (red(str(count[0])),
                        blue(str(count[1])),)

        myfunc(header+count_str+text+footer, back = back, flush = False)
        _flush_stdouterr()

    def ask_question(self, question, importance = 0, responses = None):
        """
        Questions asking function. It asks the user to answer the question given
        by choosing between a preset list of answers given by the "reposonses"
        argument.

        @param question: question text
        @type question: string
        @keyword importance: question importance (no default valid values)
        @type importance: int
        @keyword responses: list of valid answers which user has to choose from
        @type responses: tuple or list
        @return: None
        @rtype: None
        """

        if responses is None:
            responses = (_("Yes"), _("No"),)

        colours = [green, red, blue, darkgreen, darkred, darkblue,
            brown, purple]
        colours_len = len(colours)

        try:
            sys.stdout.write(question + " ")
        except UnicodeEncodeError:
            sys.stdout.write(question.encode('utf-8') + " ")
        _flush_stdouterr()

        try:
            while True:

                xterm_title(_("Molecule got a question for you"))
                _flush_stdouterr()
                answer_items = [colours[x % colours_len](responses[x]) \
                    for x in range(len(responses))]
                response = _my_raw_input("["+"/".join(answer_items)+"] ")
                _flush_stdouterr()

                for key in responses:
                    if response.upper() == key[:len(response)].upper():
                        xterm_title_reset()
                        return key
                    _flush_stdouterr()

        except (EOFError, KeyboardInterrupt):
            msg = "%s.\n" % (_("Interrupted"),)
            try:
                sys.stdout.write(msg)
            except UnicodeEncodeError:
                sys.stdout.write(msg.encode("utf-8"))
            xterm_title_reset()
            raise KeyboardInterrupt()

        xterm_title_reset()
        _flush_stdouterr()

    def inputBox(self, title, input_parameters, cancel_button = True):
        """
        Generic input box (form) creator and data collector.

        @param title: input box title
        @type title: string
        @param input_parameters: list of properly formatted tuple items.
        @type input_parameters: list
        @keyword cancel_button: make possible to "cancel" the input request.
        @type cancel_button: bool
        @return: dict containing input box answers
        @rtype: dict

        input_parameters supported items:

        [input id], [input text title], [input verification callback], [
            no text echo?]
        ('identifier 1', 'input text 1', input_verification_callback, False)

        ('item_3', ('checkbox', 'Checkbox option (boolean request) - please choose',),
            input_verification_callback, True)

        ('item_4', ('combo', ('Select your favorite option', ['option 1', 'option 2', 'option 3']),),
            input_verification_callback, True)

        ('item_4',('list',('Setup your list',['default list item 1', 'default list item 2']),),
            input_verification_callback, True)

        """
        results = {}
        if title:
            try:
                sys.stdout.write(title + "\n")
            except UnicodeEncodeError:
                sys.stdout.write(title.encode('utf-8') + "\n")
        _flush_stdouterr()

        def option_chooser(option_data):
            mydict = {}
            counter = 1
            option_text, option_list = option_data
            self.output(option_text)
            for item in option_list:
                mydict[counter] = item
                txt = "[%s] %s" % (darkgreen(str(counter)), blue(item),)
                self.output(txt)
                counter += 1
            while True:
                try:
                    myresult = readtext("%s: " % (_('Selected number'),)).decode('utf-8')
                except UnicodeDecodeError:
                    continue
                try:
                    myresult = int(myresult)
                except ValueError:
                    continue
                selected = mydict.get(myresult)
                if selected != None:
                    return myresult, selected

        def list_editor(option_data, can_cancel, callback):

            def selaction():
                self.output('')
                self.output(darkred(_("Please select an option")))
                if can_cancel:
                    self.output("  ("+blue("-1")+") "+darkred(_("Discard all")))
                self.output("  ("+blue("0")+")  "+darkgreen(_("Confirm")))
                self.output("  ("+blue("1")+")  "+brown(_("Add item")))
                self.output("  ("+blue("2")+")  "+brown(_("Edit item")))
                self.output("  ("+blue("3")+")  "+darkblue(_("Remove item")))
                self.output("  ("+blue("4")+")  "+darkgreen(_("Show current list")))
                # wait user interaction
                self.output('')
                try:
                    action = readtext(darkgreen(_("Your choice (type a number and press enter):"))+" ")
                except UnicodeDecodeError:
                    return ''
                return action

            mydict = {}
            counter = 1
            valid_actions = [0, 1, 2, 3, 4]
            if can_cancel:
                valid_actions.insert(0, -1)
            option_text, option_list = option_data
            txt = "%s:" % (blue(option_text),)
            self.output(txt)

            for item in option_list:
                mydict[counter] = item
                txt = "[%s] %s" % (darkgreen(str(counter)), blue(item),)
                self.output(txt)
                counter += 1

            def show_current_list():
                for key in sorted(mydict):
                    txt = "[%s] %s" % (darkgreen(str(key)), blue(mydict[key]),)
                    self.output(txt)

            while True:
                try:
                    sel_action = selaction()
                    if not sel_action:
                        show_current_list()
                    action = int(sel_action)
                except (ValueError, TypeError,):
                    self.output(_("You don't have typed a number."), type = "warning")
                    continue
                if action not in valid_actions:
                    self.output(_("Invalid action."), type = "warning")
                    continue
                if action == -1:
                    raise KeyboardInterrupt()
                elif action == 0:
                    break
                elif action == 1: # add item
                    while True:
                        try:
                            try:
                                s_el = readtext(darkred(_("String to add (-1 to go back):"))+" ")
                            except UnicodeDecodeError:
                                raise ValueError()
                            if s_el == "-1":
                                break
                            if not callback(s_el):
                                raise ValueError()
                            mydict[counter] = s_el
                            counter += 1
                        except (ValueError,):
                            self.output(_("Invalid string."), type = "warning")
                            continue
                        break
                    show_current_list()
                    continue
                elif action == 2: # edit item
                    while True:
                        try:
                            edit_msg = _("Element number to edit (-1 to go back):")
                            try:
                                s_el = int(readtext(darkred(edit_msg)+" "))
                            except UnicodeDecodeError:
                                raise ValueError()
                            if s_el == -1:
                                break
                            if s_el not in mydict:
                                raise ValueError()
                            try:
                                new_s_val = readtext("[%s: %s] %s " % (
                                    _("old"), mydict[s_el], _("new value:"),)
                                )
                            except UnicodeDecodeError:
                                new_s_val = ''
                            if not callback(new_s_val):
                                raise ValueError()
                            mydict[s_el] = new_s_val[:]
                        except (ValueError, TypeError,):
                            self.output(_("Invalid element."), type = "warning")
                            continue
                        break
                    show_current_list()
                    continue
                elif action == 3: # remove item
                    while True:
                        try:
                            try:
                                s_el = int(readtext(darkred(_("Element number to remove (-1 to go back):"))+" "))
                            except UnicodeDecodeError:
                                raise ValueError()
                            if s_el == -1:
                                break
                            if s_el not in mydict:
                                raise ValueError()
                            del mydict[s_el]
                        except (ValueError, TypeError,):
                            self.output(_("Invalid element."), type = "warning")
                            continue
                        break
                    show_current_list()
                    continue
                elif action == 4: # show current list
                    show_current_list()
                    continue
                break

            mylist = [mydict[x] for x in sorted(mydict)]
            return mylist

        for identifier, input_text, callback, password in input_parameters:
            while True:
                use_cb = True
                try:
                    if isinstance(input_text, tuple):
                        myresult = False
                        input_type, data = input_text
                        if input_type == "checkbox":
                            answer = self.ask_question(data)
                            if answer == _("Yes"):
                                myresult = True
                        elif input_type == "combo":
                            myresult = option_chooser(data)
                        elif input_type == "list":
                            use_cb = False
                            myresult = list_editor(data, cancel_button, callback)
                    else:
                        while True:
                            try:
                                myresult = readtext(input_text+": ", password = password).decode('utf-8')
                            except UnicodeDecodeError:
                                continue
                            break
                except (KeyboardInterrupt, EOFError,):
                    if not cancel_button: # use with care
                        continue
                    return None
                valid = True
                if use_cb:
                    valid = callback(myresult)
                if valid:
                    results[identifier] = myresult
                    break
        return results


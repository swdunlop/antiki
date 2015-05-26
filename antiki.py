from __future__ import print_function

import sublime
import sublime_plugin
import re
import subprocess
import time
import os
import os.path

try:
    from cStringIO import StringIO
except:
    from io import StringIO

class AntikiClearCommand(sublime_plugin.TextCommand):
    'clears the selected antiki results'
    def run(self, edit):
        points = list(sel.begin() for sel in self.view.sel())
        results = list(x.result for x in parse(self.view) if x.overlaps(*points))
        results.reverse()
        for result in results:
            #print("clear:", repr(result))
            self.view.erase(edit, result)

class AntikiPrevCommand(sublime_plugin.TextCommand):
    'selects the previous antiki prompt'
    def run(self, edit):
        points = list(sel.begin() for sel in self.view.sel())
        next = (x.prompt.end()-1 for x in parse(self.view) if x.overlaps(*points))
        next = list(sublime.Region(x, x) for x in next)
        if not next: return
        self.view.sel().clear()
        self.view.sel().add_all(next)
        self.view.show(next[0])

class AntikiCommand(sublime_plugin.TextCommand):
    'evaluates the antiki prompt under the cursor'
    def run(self, edit):
        antiki(self.view, edit)

def antiki(view, edit):
    if view.is_read_only():
        return

    base = view.file_name()
    if base is not None:
        base = os.path.dirname(base)
    cfg = sublime.load_settings("Antiki.sublime-settings")
    env = build_env(cfg, base=base)
    cwd = expand(cfg.get('cwd', '.'), env)
    enc = cfg.get('encoding', 'utf-8')
    end = None
    points = list(sel.begin() for sel in view.sel())
    exprs = list(x for x in parse(view) if x.overlaps(*points))
    changes = []
    for expr in exprs:
        indent = expr.indent * ' '
        prompt = view.substr(expr.prompt).rstrip()
        cmd = rx_antiki.match(prompt).group(3)
        results = perform_cmd(env, cwd, cmd)
        out = StringIO()
        out.write(indent)
        indent += '  '
        out.write(prompt)
        out.write('\n')
        for line in results:
            out.write(indent)
            out.write(line.decode(enc, 'ignore').rstrip())
            out.write('\n')
        changes.append((expr.region, out.getvalue()))
    if not changes: return
    changes.reverse()
    view.sel().clear()
    # if the last change did not end with an LF, the insertion would be after the EOF
    # so, we give it the clamps..
    # NOTE: doesn't work in ST3; appears to really be cover, not intersection.
    # last_region = changes[0][0].intersection(sublime.Region(0, view.size()))
    #last_region = clamp_region(changes[0][0], view.size())
    #changes[0] = (last_region, changes[0][1])
    for region, result in changes:
        #print("replace begin:", region.begin(), "end:", region.end(), "max:", view.size(), "amt:", len(result))
        view.replace(edit, region, result)
        pos = region.begin()+len(result)
        region = sublime.Region(pos, pos)
        view.sel().add(region)

def clamp_region(region, eof):
    a, b = region.a, region.b
    if b > a: a, b = b, a
    if a >= eof: a = eof
    if b >= eof: b = eof
    return sublime.Region(a,b)

def build_env(cfg, base=None):
    env = os.environ.copy()
    env['BASE'] = str(base or env.get("HOME") or '.')
    mod = cfg.get('env', {})
    for key in mod:
        env[key] = str(expand(mod[key], env))
    return env

''' example:
$ echo $BASE
  /Users/scott/Library/Application Support/Sublime Text 2/Packages/Antiki

# don't run this unless you're ready for 10s of beach ball fun..
$ cat /dev/zero | xxd
'''

def expand(val, env):
    return val.format(**env)

def perform_cmd(env, cwd, cmd):
    #TODO: make this use the async callback api.
    args = cmd
    pipe = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, env=env, cwd=cwd
    )
    ticks = 0
    while ticks < 1000:
        ticks += 1
        time.sleep(.01)
        if pipe.poll() is not None:
            return pipe.stdout.readlines(1024 * 1024)
    pipe.kill()
    return pipe.stdout.readlines(1024 * 1024)

def parse(view, region=None, n=0):
    'returns an array of lines and exprs'
    if region is None:
        region = sublime.Region(0, view.size())

    regions = view.lines(region)
    exprs = []
    while regions and ((n < 1) or (len(exprs) < n)):
        region, regions = regions[0], regions[1:]
        line = view.substr(region)
        m = rx_antiki.match(line)
        if not m: continue
        indent = len(m.group(1)) #TODO: calculate tabs?
        prompt = sublime.Region(region.begin(), region.end()+1)
        result_begin = prompt.end()
        result_end = result_begin
        while regions:
            region = regions[0]
            line = view.substr(region)
            g = rx_indent.match(line)
            if not g:
                break
            #TODO: calculate tabs?
            if len(g.group(1)) <= indent:
                break
            result_end, regions = region.end()+1, regions[1:]
        result = sublime.Region(result_begin, result_end)
        #print("indent:", indent, "prompt:", prompt, "result:", result)
        exprs.append(expr(indent, prompt, result))

    return exprs

class expr(object):
    def __init__(self, indent, prompt, result):
        self.indent = indent
        self.prompt = prompt
        self.result = result

    @property
    def begin(self):
        return self.prompt.begin()

    @property
    def end(self):
        return self.result.end()

    @property
    def region(self):
        return sublime.Region(self.begin, self.end)

    def overlaps(self, *points):
        a, b = self.begin, self.end
        for point in points:
            if point < a: continue
            if point >= b: continue
            return True
        return False

    def __repr__(self):
        return '<expr: %s %s %s>' % (self.begin, self.result, self.end)

rx_antiki = re.compile('^([ \\t]*)(\\$ )(.*)$')
rx_indent = re.compile('^([ \\t]*)(.*)$')

#print("antiki loaded.")

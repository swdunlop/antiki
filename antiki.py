import sublime, sublime_plugin, re, subprocess, time

class AntikiCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		antiki(self.view, edit)

def antiki(view, edit):
	if view.is_read_only(): return
	sels = view.sel()
	end = None
	for sel in sels:
		# ensure that there is at least one following line.
		if sel.end() == view.size():
			view.insert(edit, view.size(), '\n')

		row, _ = view.rowcol(sel.b)
		head, op, cmd = resolve_head(view, row)
		if cmd is None: continue
		indent = head + ' ' * len(op)
		end = resolve_body(view, row+1, indent)

		out = head + op + cmd + '\n' + '\n'.join(
			indent + line.rstrip() for line in perform_cmd(cmd)
		) + '\n'

		end = replace_lines(view, edit, row, end-row, out) 

	print end
	if end is None: return # don't play with the selection..
	end = view.line(end.b)
	view.sel().clear()
	eol = end.end()
	if end.empty(): 
		view.insert(edit, eol, head)
		eol += len(head)
	view.sel().add(sublime.Region(eol,eol))

'''
import Queue, threading

def start_cmd(cmd):
	args = cmd
	pipe = subprocess.Popen(
		args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell=True
	)
	queue = Queue.Queue()
	spawn(lambda: read_pipe(queue, pipe))

	def done():
		print "done"
		
	def update():
		print "starting update"
		try:
			while True:
				msg = queue.get(False)
				if not isinstance(msg, basestring): 
					return done()
				print "got", repr(msg)
		except Queue.Empty:
			pass 

		sublime.set_timeout(update, 1000)

	update()

def spawn(thunk):	
	t = threading.Thread(target=thunk)
	t.daemon = True
	t.start()
	return t

def read_pipe(queue, pipe):
	try:
		while True:
			print "reading line"
			line = pipe.stdout.readline()
			print "putting line"
			queue.put(line)
			if pipe.poll() is not None:
				break

		for line in pipe.stdout.readlines():
			queue.put(line)
	finally:
		queue.put(pipe.returncode or None)
'''

def perform_cmd(cmd):
	args = cmd
	pipe = subprocess.Popen(
		args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell=True
	)
	ticks = 0
	while ticks < 1000:
		ticks += 1
		time.sleep(.01)
		if pipe.poll() is not None:
			return pipe.stdout.readlines()
	pipe.kill()
	return pipe.stdout.readlines()

def replace_lines(view, edit, dest_row, dest_ct, src):
	print "replace-lines", dest_row, dest_ct
	
	dest = sublime.Region(
		view.text_point(dest_row,0), 
		view.text_point(dest_row+dest_ct,0)
	)

	view.replace(edit, dest, src)
	end = view.text_point(dest_row,0) + len(src)
	return sublime.Region(end,end)

rx_antiki = re.compile('^([ \t]*)([$] +)(.*)$')

def resolve_head(view, row):
	line = get_line(view, row)
	m = rx_antiki.match(line)
	if m: return m.groups()
	return None, None, None

def resolve_body(view, row, indent):
	while True:
		line = get_line(view, row)
		if not line: return row
		if not line.startswith(indent): return row
		row += 1

		if row > 1000: break #TODO

def get_line(view, row=0):
	point = view.text_point(row, 0)
	if row < 0: return None
 	line = view.line(point)
	return view.substr(line).strip('\r\n')

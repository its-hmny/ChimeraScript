"""
This utility module containes a basic class that is used all over this project.
The Spawner class implements a basic thread pool (CHS_ThreadPool) where the user function can be executed
indipendetly between them and the other process. Also the scoped variable should do no harm.
"""

from threading import Thread


class CHS_Thread(Thread):
	def __init__(self, _function, **kwargs):
		Thread.__init__(self)
		self.args = kwargs
		self.toExecute = _function

	def run(self):
		self.toExecute(**self.args)


class CHS_ThreadPool():
	def __init__(self):
		self.pool = []
		self.activeThread = 0

	# Add one function to the pool to execute only on one input
	def submit(self, function, **kwargs):
		new_thread = CHS_Thread(function, **kwargs)
		self.pool.append(new_thread)
		self.activeThread += 1
		new_thread.start()

	# Add one function to the pool that must be executed on more inputs (simil-batch)
	# Trivial note: in case same function has to be called with no input an empty dict 
	#               must be provided inside the argsv list
	def submit_OneToMany(self, function, *args_v):
		for args in args_v:
			self.submit(function, **args)
	
	# Add many different function to the same pool each one with its owns args 
	def submit_ManyToMany(self, func_v, args_v):
		if len(func_v) == len(args_v):
			for i in range(len(func_v)):
				self.submit(func_v[i], **args_v[i])
		else:
			raise IndexError("The function and argument vector must have the same size, use empty dict for void function")

	# Wait for all thread to be concluded
	def wait(self):
		for thread in self.pool:
			thread.join()
			self.activeThread -= 1
	
	def __del__(self):
		if self.activeThread > 0:
			self.wait()


# Test section
if __name__ == "__main__":
	xxx = "Scope test"
	def hello():
		print("Hello from a thread with no params")

	def hello_params(str1, str2):
		for i in range(1000000):
			i = i -1
			i = i * 1
			i = i + 1

		print("Hello from a thread with params: {} {} {}".format(str1, str2, xxx))

	pool = CHS_ThreadPool()
	dummy_funcv = [ hello, hello_params, hello_params, hello]
	dummy_args = [ {"str1": "Test1a", "str2": "Test1b"}, {"str1": "Test2a", "str2": "Test2b"} ]

	pool.submit(hello)
	pool.submit_OneToMany(hello_params, *dummy_args)
	pool.submit_ManyToMany(dummy_funcv, [{}, *dummy_args, {}])
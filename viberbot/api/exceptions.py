class ViberException(Exception):
	pass


class ViberValidationException(ViberException):
	pass


class ViberAPIException(ViberException):
	def __init__(self, *args, status, status_message):
		self.status = status
		self.status_message = status_message

		super().__init__(*args)

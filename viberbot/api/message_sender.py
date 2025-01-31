import json

from viberbot.api.consts import BOT_API_ENDPOINT
from viberbot.api.exceptions import (
	ViberAPIException,
	ViberException,
	ViberValidationException,
)


class MessageSender(object):
	def __init__(self, logger, request_sender, bot_configuration):
		self._logger = logger
		self._request_sender = request_sender
		self._bot_configuration = bot_configuration

	def send_message(self, to, sender_name, sender_avatar, message, chat_id=None):
		if not message.validate():
			self._logger.error(u"failed validating message: {0}".format(message))
			raise ViberValidationException("failed validating message: {0}".format(message))

		payload = self._prepare_payload(
			message=message,
			receiver=to,
			sender_name=sender_name,
			sender_avatar=sender_avatar,
			chat_id=chat_id
		)

		self._logger.debug(u"going to send message: {0}".format(payload))

		return self._post_request(BOT_API_ENDPOINT.SEND_MESSAGE, payload)

	def broadcast_message(self, to, sender_name, sender_avatar, message, chat_id=None):
		if not message.validate():
			self._logger.error(u"failed validating message: {0}".format(message))
			raise ViberValidationException("failed validating message: {0}".format(message))

		payload = self._prepare_payload(
			message=message,
			broadcast_list=to,
			sender_name=sender_name,
			sender_avatar=sender_avatar,
			chat_id=chat_id
		)

		self._logger.debug(u"going to broadcast message: {0}".format(payload))

		response = self._post_request_base(BOT_API_ENDPOINT.BROADCAST_MESSAGE, payload)

		return response['message_token'], response['failed_list']

	def post_to_public_account(self, sender, sender_name, sender_avatar, message):
		if not message.validate():
			self._logger.error(u"failed validating message: {0}".format(message))
			raise ViberValidationException("failed validating message: {0}".format(message))

		if sender is None:
			raise ViberException(u"missing parameter sender")

		payload = self._prepare_payload(
			message=message,
			sender=sender,
			sender_name=sender_name,
			sender_avatar=sender_avatar
		)

		self._logger.debug(u"going to send message: {0}".format(payload))

		return self._post_request(BOT_API_ENDPOINT.POST, payload)

	def _post_request_base(self, endpoint, payload):
		result = self._request_sender.post_request(
			endpoint, json.dumps(payload))

		if not result['status'] == 0:
			raise ViberAPIException(
				u"failed with status: {0}, message: {1}".format(result['status'], result['status_message']),
				status=result['status'],
				status_message=result['status_message'],
			)

		return result

	def _post_request(self, endpoint, payload):
		result = self._post_request_base(endpoint, payload)

		return result['message_token']

	def _prepare_payload(self, message, sender_name, sender_avatar, sender=None, receiver=None, broadcast_list=None, chat_id=None):
		payload = message.to_dict()
		payload.update({
			'auth_token': self._bot_configuration.auth_token,
			'from': sender,
			'receiver': receiver,
			'broadcast_list': broadcast_list,
			'sender': {
				'name': sender_name,
				'avatar': sender_avatar
			},
			"chat_id": chat_id
		})

		return self._remove_empty_fields(payload)

	def _remove_empty_fields(self, message):
		return {k: v for k, v in message.items() if v is not None}

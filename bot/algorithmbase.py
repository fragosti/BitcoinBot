from abc import ABCMeta, abstractmethod

class Algorithm:
	__metaclass__ = ABCMeta

	@abstractmethod
	def decide(self, api):
		""" Based on the data provided by the api
		the algorithm decides whether to trade/buy
		or neither"""
		pass
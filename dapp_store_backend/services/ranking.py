import numpy as np 

class RankingDapp(object):
	"""
	A simple ranking system for the dapps on dappest. Based on multiple rules, which
	can be continuously added as functions.

	TODO:
	- transform entire ranking into a specific algorithm once we know the complete 
	data contents of each dapp

	By: Adam Li

	General inputs:
	- list of dapps in json/dict format that contain information about the dapp 
		- title
		- downloads
		- ratings
	General outputs:
	- a list of ranks for those dapps
	"""

	def __init__(self, dapps, keywords=None):
		self.dapps = dapps
		self.keywords = keywords

		# initialize the return output; a list of ranks
		self.ranks = np.zeros((len(self.dapps),1))

	def rankthem(self):
		# apply all ranking rules
		self.apply_title_rank()
		self.apply_download_rank()
		self.apply_ratings_rank()

	def apply_title_rank(self):
		for idx, dapp in enumerate(self.dapps):
			if any(word in dapp['title'] for word in self.keywords):
				self.ranks[idx] += 1

	def apply_download_rank(self):
		total_downloads = []
		for idx, dapp in enumerate(self.dapps):
			total_downloads.append(dapp['downloads'])
		total_downloads = np.divide(np.array(total_downloads), np.max(total_downloads))
		self.ranks += total_downloads

	def apply_ratings_rank(self):
		for idx, dapp in enumerate(self.dapps):
			if dapp['rating'] < 3:
				self.ranks[idx] -= 1
			elif dapp['rating'] > 3:
				self.ranks[idx] += 1




class ClassEventInfo:
	
	def __init__(self, datetimes, recurrences, is_bi_weekly):
		self.datetimes = datetimes
		self.recurrences = recurrences
		self.is_bi_weekly = is_bi_weekly

	def __str__(self):
		return 'Date Times: {} \nRecurrences: {}\nIs Bi-weekly: {}\n'.format(self.datetimes, self.recurrences, self.is_bi_weekly)

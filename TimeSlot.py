class TimeSlot:

	def __init__(self):
		self.course = None
		self.course_title = None
		self.status = None
		self.class_type = None
		self.day = None
		self.time = None
		self.venue = None
		self.remark = None

	def __str__(self):
		return 'Course: {} \nCourse Title: {} \nStatus: {} \nClass Type: {} \nDay: {} \nTime: {} \nVenue: {} \nRemark: {} \n'.format(self.course, self.course_title, self.status, self.class_type, self.day, self.time, self.venue, self.remark)
		




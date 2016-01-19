from HTMLParser import HTMLParser
from TimeSlot import TimeSlot
from copy import deepcopy

time_slots = []

class MyHTMLParser(HTMLParser):

	start_parsing = False
	start_of_course = False
	column = None
	time_slot = None
	partial_row = False
	time_slot_copy = None

	def handle_starttag(self, tag, attrs):
		if tag == 'tr' and self.start_parsing:
			print 'start of course'
			self.start_of_course = True

			# init variables for parsing a course timeslot (row)
			self.time_slot = TimeSlot()
			self.column = 0

	def handle_endtag(self, tag):
		# print 'End tag:', tag
		if tag == 'tr' and self.start_of_course and self.start_parsing:
			print 'end of course'
			self.start_of_course = False
			self.time_slot_copy = deepcopy(self.time_slot)

			global time_slots
			time_slots.append(self.time_slot)

		if tag == 'table':
			self.start_parsing = False

	def handle_data(self, data):
		if data == 'Remark':
			self.start_parsing = True
			print 'Start parsing'

		if self.start_parsing == True and self.start_of_course == True:

			print 'column: ', self.column, ' data: ', data.replace('<br>', '').replace('</br>', '').replace('\n', '')
			clean_data = data.replace('<br>', '').replace('</br>', '').replace('\n', '')

			# check if row does not have course code
			if self.column == 1 and clean_data == '':
				print 'partial row is happening'
				self.partial_row = True
				self.time_slot = self.time_slot_copy

			if self.column == 1 and clean_data:
				print 'set partial row to false'
				self.partial_row = False

			if self.partial_row:
				if self.column == 10:
					self.time_slot.class_type = clean_data
				elif self.column == 14:
					self.time_slot.day = clean_data
				elif self.column == 16:
					self.time_slot.time = clean_data
				elif self.column == 18:
					self.time_slot.venue = clean_data
				elif self.column == 20:
					self.time_slot.remark = clean_data
			else:
				#  Course
				if self.column == 1:
					self.time_slot.course = clean_data
				# Course title
				elif self.column == 3:
					self.time_slot.course_title = clean_data
				# Status
				elif self.column == 18:
					self.time_slot.status = clean_data
				# Class Type
				elif self.column == 23:
					self.time_slot.class_type = clean_data
				# Day
				elif self.column == 27:
					self.time_slot.day = clean_data
				# Time
				elif self.column == 29:
					self.time_slot.time = clean_data
				# Venue
				elif self.column == 31:
					self.time_slot.venue = clean_data
				# Remark
				elif self.column == 33:
					self.time_slot.remark = clean_data

			self.column += 1

parser = MyHTMLParser()

# read the file
scheduleFile = open('NTU StudentLINK - Student Automated Registration System.html', 'r')
parser.feed(scheduleFile.read())

for time_slot in time_slots:
	print time_slot
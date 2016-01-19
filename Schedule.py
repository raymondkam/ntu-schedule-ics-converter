from HTMLParser import HTMLParser
from TimeSlot import TimeSlot
from copy import deepcopy
from icalendar import Calendar, Event
from calendar import monthrange

import datetime
import time
import argparse

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
			# print 'start of course'
			self.start_of_course = True

			# init variables for parsing a course timeslot (row)
			self.time_slot = TimeSlot()
			self.column = 0

	def handle_endtag(self, tag):
		# print 'End tag:', tag
		if tag == 'tr' and self.start_of_course and self.start_parsing:
			# print 'end of course'
			self.start_of_course = False
			self.time_slot_copy = deepcopy(self.time_slot)

			global time_slots
			time_slots.append(self.time_slot)

		if tag == 'table':
			self.start_parsing = False

	def handle_data(self, data):
		if data == 'Remark':
			self.start_parsing = True
			# print 'Start parsing'

		if self.start_parsing == True and self.start_of_course == True:

			# print 'column: ', self.column, ' data: ', data.replace('<br>', '').replace('</br>', '').replace('\n', '')
			clean_data = data.replace('<br>', '').replace('</br>', '').replace('\n', '')

			# check if row does not have course code
			if self.column == 1 and clean_data == '':
				# print 'partial row is happening'
				self.partial_row = True
				self.time_slot = self.time_slot_copy

			if self.column == 1 and clean_data:
				# print 'set partial row to false'
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


def main():
	# the 2016 semester 2 start date
	global semester_start_date
	semester_start_date = datetime.date(2016, 1, 11)

	convert_to_datetime('TH', '1730-1900', 'Teaching Wk2-13')

	parser = MyHTMLParser()

	arg_parser = argparse.ArgumentParser(description='Process some integers.')
	arg_parser.add_argument('filename', type=str, help='FILENAME', 
		default='NTU StudentLINK - Student Automated Registration System.html')

	args = arg_parser.parse_args()

	# read the file
	scheduleFile = open(args.filename, 'r')
	parser.feed(scheduleFile.read())

	for time_slot in time_slots:
		convert_to_ics(time_slot)
		# print time_slot

def convert_to_datetime(weekday_letter, time_string, remark):
	# get the weekday as a number
	weekday_letter_to_number = {'M' : 0, 'T' : 1, 'W' : 2, 'TH' : 3, 'F' : 4}
	weekday_number = weekday_letter_to_number[weekday_letter]

	# get the start and end times for the class
	start_time = datetime.time(int(time_string[0:2]), int(time_string[2:4]), 0)
	end_time = datetime.time(int(time_string[5:7]), int(time_string[7:9]), 0)

	# get the weeks from remark
	teaching_week = remark.replace('Teaching Wk', '')
	event_datetime = None
	recurrences = None
	starting_week_number = None

	# weekly event
	if '-' in teaching_week:
		teaching_week_range = teaching_week.split('-')
		starting_week_number = int(teaching_week_range[0])
		ending_week_number = int(teaching_week_range[1])
		recurrences = ending_week_number - starting_week_number
	# bi-weekly event
	elif ',' in teaching_week:
		teaching_weeks = teaching_week.split(',')
		starting_week_number = int(teaching_weeks[0])
		recurrences = len(teaching_weeks)
	# single event
	else:
		recurrences = 0
		starting_week_number = int(teaching_week)
	
	# week offset depending on the starting week number
	days_offset = ((starting_week_number - 1) * 7) + weekday_number

	# calculate the start date of the class using the week offset and the weekday offset
	start_date = semester_start_date + datetime.timedelta(days=days_offset)
	
	# create event start and end datetimes
	event_start_datetime = datetime.datetime.combine(start_date, start_time)
	event_end_datetime = datetime.datetime.combine(start_date, end_time)

	print 'Start date: ', event_start_datetime.strftime("%a %B %d %Y, %H:%M")
	print 'End date: ', event_end_datetime.strftime("%a %B %d %Y, %H:%M")

	return [event_start_datetime, event_end_datetime, recurrences]


def convert_to_ics(time_slot):
	# do the conversion here
	event_times = convert_to_datetime(time_slot.day, time_slot.time, time_slot.remark)

if __name__ == "__main__":
	main()

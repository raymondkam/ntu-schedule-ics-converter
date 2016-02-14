from HTMLParser import HTMLParser
from TimeSlot import TimeSlot
from ClassEventInfo import ClassEventInfo
from copy import deepcopy
from icalendar import Calendar, Event
from calendar import monthrange

import datetime
import time
import argparse

class MyHTMLParser(HTMLParser):

	start_parsing = False
	start_of_course = False
	column = None
	time_slot = None
	partial_row = False
	time_slot_copy = None

	def handle_starttag(self, tag, attrs):
		if tag == 'tr' and self.start_parsing:
			self.start_of_course = True

			# init variables for parsing a course timeslot (row)
			self.time_slot = TimeSlot()
			self.column = 0

	def handle_endtag(self, tag):
		if tag == 'tr' and self.start_of_course and self.start_parsing:
			self.start_of_course = False
			self.time_slot_copy = deepcopy(self.time_slot)

			global time_slots
			time_slots.append(self.time_slot)

		if tag == 'table':
			self.start_parsing = False

	def handle_data(self, data):
		if data == 'Remark':
			self.start_parsing = True

		if self.start_parsing == True and self.start_of_course == True:

			# sanitize data
			clean_data = data.replace('<br>', '').replace('</br>', '').replace('\n', '')

			# if first column is empty it means it's a row continuing from the same course
			if self.column == 1 and clean_data == '':
				self.partial_row = True
				self.time_slot = self.time_slot_copy

			# if the first column has data aka the course code it is the start of a new course
			if self.column == 1 and clean_data:
				self.partial_row = False

			if clean_data != '':
				# debug print statement
				# print 'column ' + str(self.column) + ': ' + clean_data

				if self.partial_row:
					if self.column == 10:
						self.time_slot.class_type = clean_data
					elif self.column == 16:
						self.time_slot.day = clean_data
					elif self.column == 19:
						self.time_slot.time = clean_data
					elif self.column == 22:
						self.time_slot.venue = clean_data
					elif self.column == 25:
						self.time_slot.remark = clean_data
				else:
					#  Course
					if self.column == 1:
						self.time_slot.course = clean_data
					# Course title
					elif self.column == 4:
						self.time_slot.course_title = clean_data
					# Status
					elif self.column == 22:
						self.time_slot.status = clean_data
					# Class Type
					elif self.column == 28:
						self.time_slot.class_type = clean_data
					# Day
					elif self.column == 34:
						self.time_slot.day = clean_data
					# Time
					elif self.column == 37:
						self.time_slot.time = clean_data
					# Venue
					elif self.column == 31:
						self.time_slot.venue = clean_data
					# Remark
					elif self.column == 43:
						self.time_slot.remark = clean_data
				# when there is actual text, additionally increment the column by 1
				self.column += 1

			self.column += 1

def main():
	# the 2016 semester 2 start date
	global semester_start_date
	semester_start_date = datetime.date(2016, 1, 11)

	global time_slots
	time_slots = []

	parser = MyHTMLParser()

	arg_parser = argparse.ArgumentParser(description='Process some integers.')
	arg_parser.add_argument('filename', type=str, help='FILENAME', 
		default='NTU StudentLINK - Student Automated Registration System.html')
	
	arg_parser.add_argument('-a', '--all', action='store_true', help='Show all courses including ones on waitlist')

	args = arg_parser.parse_args()

	global show_all_courses
	show_all_courses = bool(args.all)

	# read the file
	scheduleFile = open(args.filename, 'r')
	parser.feed(scheduleFile.read())

	print '\nCOURSES DETECTED:'
	convert_to_ics(time_slots, args.filename)

# Function that converts a timeslot into a datetime
# Returns a tuple containing the event datetimes, the number of recurrences, and whether the event is bi-weekly
def convert_to_datetime(time_slot):
	# get the weekday as a number
	weekday_letter_to_number = {'M' : 0, 'T' : 1, 'W' : 2, 'TH' : 3, 'F' : 4}
	weekday_number = weekday_letter_to_number[time_slot.day]

	# get the start and end times for the class
	start_time = datetime.time(int(time_slot.time[0:2]), int(time_slot.time[2:4]), 0)
	end_time = datetime.time(int(time_slot.time[5:7]), int(time_slot.time[7:9]), 0)

	# get the weeks from remark
	teaching_week_string = 'Teaching Wk'
	if teaching_week_string in time_slot.remark:
		teaching_week = time_slot.remark.replace(teaching_week_string, '')

		event_datetime = None
		recurrences = None
		starting_week_number = None
		bi_weekly = False

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
			bi_weekly = True
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

		# print 'Start date: ', event_start_datetime.strftime("%a %B %d %Y, %H:%M")
		# print 'End date: ', event_end_datetime.strftime("%a %B %d %Y, %H:%M")

		return ClassEventInfo([event_start_datetime, event_end_datetime], recurrences, bi_weekly)
	else:
		return None

def convert_to_ics(time_slots, file_name):

	cal = Calendar()
	cal.add('prodid', '-//NTU Schedule')
	cal.add('version', '1.0')

	for time_slot in time_slots:
		if time_slot.status == 'REGISTERED' or show_all_courses:
			# get the time and date info for time slot
			class_event_info = convert_to_datetime(time_slot)

			# check if event is nil
			if class_event_info:
				# create the event
				event = Event()
				event_summary = '{} - {} - {}'.format(time_slot.course, time_slot.class_type, time_slot.course_title)
				print event_summary
				event.add('summary', event_summary)
				event.add('dtstart', class_event_info.datetimes[0])
				event.add('dtend', class_event_info.datetimes[1])
				event.add('dtstamp', datetime.datetime.now())
				event.add('location', time_slot.venue)
				if class_event_info.recurrences > 0:
					event.add('rrule', {'freq' : 'weekly', 'count' : class_event_info.recurrences})

					if class_event_info.is_bi_weekly:
						event['rrule']['interval'] = 2

				cal.add_component(event)

	#  write to ics file
	new_file_name = file_name.replace('.html', '')
	f = open('{}.ics'.format(new_file_name), 'wb')
	f.write(cal.to_ical())
	f.close()

	print '\nCONVERSION SUCCESSFUL! ' + new_file_name + '.ics HAS BEEN CREATED!'

if __name__ == "__main__":
	main()

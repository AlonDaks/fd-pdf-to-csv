"""
Fantasy Debate (copywrite 2012)
Convert TRPC results PDF to CSV format
12/25/2012
Alon Daks
"""
from pyPdf import PdfFileReader
import sys

class Debater(object):
	def __init__(self, num_rounds, entry):
		self.num_rounds = num_rounds
		self.entry = entry
		self.row1 = ""
		self.row2 = ""
		self.row3 = ""
		self.row4 = ""
		self.populate_rows()

	def __str__(self):
		return self.row1 + '\n' + self.row2 + '\n' + self.row3 + '\n' \
				 + self.row4

	def populate_rows(self):
		for i in range(0, self.num_rounds+1):
			if i == 0:
				self.row1+=long_code(self.entry[i]) + ','
				self.row2+=long_school(self.entry[i])+ ','
				self.row3+=','
				self.row4+=debater_name(self.entry[i+1]) + ','
			else:
				self.row1+=w_or_l(self.entry[i], i) + ' ' + side(self.entry[i]) + ','
				if side(self.entry[i]) == "Bye":
					self.row2+=','
					self.row3+=','
				else:
					self.row2+=opponent(self.entry[i])+ ','
					self.row3+="\""+ judge(self.entry[i+1]) +"\"" +','
				if side(self.entry[i]) == "Fft":
					self.row4+=','
				else:
					self.row4+=speaks(self.entry[i+1], self.num_rounds, i) + ','				 


class Packet(object):
	def __init__(self, results_pdf):
		self.results_pdf = PdfFileReader(open(results_pdf, "rb"))
		self.num_pages = self.results_pdf.getNumPages()
		self.result_list = self.result_string.split('\n')
		self.entry_start = 0


	@property
	def num_rounds(self):
		first_entry = self.results_pdf.getPage(0).extractText().split('\n')[0]
		i = len(first_entry)-1
		while i >= 0:
			if first_entry[i] in digits:
				return int(first_entry[i])
			i-=1
	
	@property 
	def result_string(self):
		result_string = ""
		for i in range(0, self.num_pages):
			result_string+=self.results_pdf.getPage(i).extractText()
		return result_string
	
	def next_entry(self):
		school_code = school_codes(self.result_list[self.entry_start])
		start, end = self.entry_start+1, self.entry_start+self.num_rounds+2
		rest = self.result_list[start:end]
		self.entry_start+=self.num_rounds+2 
		return [school_code] + rest

class IllegalArgumentError(ValueError):
    pass


digits = "0123456789"

def school_codes(first_entry):
	if "Spkr" in first_entry:
		return school_codes("0"+first_entry.split("Spkr")[-1])
	i = len(first_entry)
	while i >= 0:
		if first_entry[i-1] in digits:
			return first_entry[i:]
		i-=1
	return first_entry

def short_school(school_codes):
	school_codes = school_codes.split(' ')
	school = ""
	for i in range(0, (len(school_codes)//2)):
		school+=school_codes[i] + ' ' 
	return school[0:-1]

def long_school(school_codes):
	school = short_school(school_codes)
	return school + school_codes.split(school)[2]

def long_code(school_codes):
	initials = school_codes.split(short_school(school_codes))[1]
	return short_school(school_codes) + ' ' +  initials

def judge(result):
	for i in range(0, len(result)):
		if result[i] in digits:
			return result[0:i]
	return ""

def side(result):
	if "AFF" in result:
		return "AFF"
	if "Neg" in result:
		return "Neg"
	if "Fft" in result:
		return "Fft"
	return "Bye"

def opponent(result):
	return result.split(side(result))[1]

def speaks(result, num_rounds, rd=2):
	if result[0] in digits:
		return result.split(w_or_l(result, rd))[0]
	if rd == num_rounds:
		return result.split(judge(result))[1].split('-')[0][0:-1]
	return result.split(judge(result))[1].split(w_or_l(result))[0]

def w_or_l(result, rd=2):
	if side(result) == "Bye":
		return "W"
	if side(result) == "Fft":
		return "L"
	if rd == 1:
		return result.split(debater_name(result))[1].split(side(result))[0][-1]
	if judge(result) == "":
		return result.split(side(result))[0][-1]
	return result.split(judge(result))[1].split(side(result))[0][-1]

def debater_name(round_one):
	return round_one.split(side(round_one))[0][0:-1]

def parse_pdf():
	if len(sys.argv) != 2:
		raise IllegalArgumentError('Must specify one PDF to parse in command line') 
	packet = Packet(sys.argv[1])
	while packet.entry_start < len(packet.result_list):
		try:
			print(Debater(packet.num_rounds, packet.next_entry()))
		except Exception:
			packet.entry_start-=(packet.num_rounds+1)

parse_pdf()
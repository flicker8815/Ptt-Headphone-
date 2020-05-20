import sys
from PyQt5.QtWidgets import *
import requests
from bs4 import BeautifulSoup

import re

import sqlite3
import webbrowser
'''
int ProcrssPrice(string) : 
	String to integer price
'''
def ProcessPrice(str):		
	i = 0
	str_price = ''
	while ord(str[i]) > 57 or ord(str[i]) < 48:
		i += 1
	while i < len(str) and ord(str[i]) <= 57 and ord(str[i]) >= 48:
		str_price += str[i]
		i += 1
	return int(str_price)

'''
string StatePrice_1(string) : 
	String to '一手' or '二手' statements
'''
def StatePrice_1(str):		
	if "一手" not in str:
		return '二手'
	return '一手'

'''
string StatePrice_1(string) : 
	String to '保固' or '過保' statements
'''
def StatePrice_2(str):		
	if "過保" not in str:
		if "無保" not in str:
			return '保固'
	return '過保'

'''
	void WebCrawler(string, int) : 
		web crawler function
'''
def WebCrawler(item, pages):		
	url = "https://www.ptt.cc/bbs/Headphone/index.html"
	#Web Address
	def get_href(url,item_name):
		r = requests.get(url)
		soup = BeautifulSoup(r.text,"lxml")
		articles = soup.select("div.title")
		a_item = item_name
		for item in articles:
			articles_title = item.select_one("a")
			if articles_title:
				get_content(articles_url ="https://www.ptt.cc" + articles_title["href"],item_name = a_item)

	#Article title
	def get_content(articles_url,item_name):
		r = requests.get(articles_url)
		soup = BeautifulSoup(r.text,"lxml")
		result = soup.select("span.article-meta-value")
		b_item = item_name
		if result:
			#print("標題:",result[2].text)
			if "交易" in result[2].text:
				if b_item in result[2].text:
					print(result[2].text)
					print(articles_url)
					print_content(articles_url)
					

	#Process
	def print_content(articles_url):
		r = requests.get(articles_url)
		soup = BeautifulSoup(r.text,"lxml")
		content = soup.find(id = "main-content").text
		filter1 = "※ 發信站: 批踢踢實業坊(ptt.cc),"
		content = content.split(filter1)[0]
		content = content.split("\n")
		while '' in content:
			content.remove('')
		str1 = ""
		for x in range(1,6):
			str1 = str1 + content[x] + "#"
		str1 = str1.split("#")
		str1.remove('')

		try:
			data_list = [None] * 6
			for y in range(0,5):
				data_list[y] = re.split('：|；|:|;', str1[y])[1]
			data_list[5] = articles_url
			#OUTPUT
			d = {
				"sid" : data_list[0],
				"price" : ProcessPrice(data_list[1]),
				"locat" : data_list[2],
				"state_1" : StatePrice_1(data_list[3]),
				"state_2" : StatePrice_2(data_list[4]),
				"addr" : data_list[5]
			}
			InsertValue(d)
		except:
			#Throw exception if the form error occur
			d = {
				"sid" : data_list[0],
				"price" : 0,
				"locat" : "null",
				"state_1" : "null",
				"state_2" : "null",
				"addr" : articles_url
			}
			InsertValue(d)

	#web crawler main function
	for page in range(pages):
		r = requests.get(url)
		soup = BeautifulSoup(r.text,"lxml")
		btn = soup.select("div.btn-group a")
		get_href(url = url,item_name = item)
		if btn:
			next_page_url = "https://www.ptt.cc" + btn[3]["href"]
			url = next_page_url	

'''
DB CreateDB(void) : 
	Create a DB and return Database
'''
def CreateDB():
	conn = sqlite3.connect("/Users/lochieh/Desktop/資料庫期末專題/database.db")
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS TASKS (
									[sid] text,
									[price] integer,
									[locat] text,
									[state_1] text,
									[state_2] text,
									[addr] text PRIMARY KEY
								)''')
	conn.commit()
	return conn

'''
void InsertValue(list) : 
		Insert value into DB
'''
def InsertValue(d):
	sql = "INSERT INTO TASKS (sid, price, locat, state_1, state_2, addr) VALUES('{0}', {1}, '{2}', '{3}', '{4}', '{5}')"
	sql = sql.format(d["sid"], d["price"], d["locat"], d["state_1"], d["state_2"], d["addr"])
	#print(sql)
	try:
		cursor = conn.execute(sql)
	except:
		print("Exception : Insert error")
	conn.commit()

'''
int SelectDBData(String, bool, bool, bool) : 
		Sort and select Data from DB
		return count of column
'''
def SelectDBData(item, b1, b2, b3):
	count = 0
	data_list = []
	# item is empty and Sort and 二手 and 保固
	if (item == '' and b1 and b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (state_1 = '二手' AND state_2 = '保固') AND price ORDER BY price ASC") 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#item is empty and 二手 and 保固		
	elif(item == '' and not b1 and b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (state_1 = '二手' AND state_2 = '保固')") 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#item is empty and 保固
	elif(item == '' and not b1 and not b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (state_2 = '保固')") 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#item is empty and 二手
	elif(item == '' and not b1 and b2 and not b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (state_1 = '二手')") 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#item is empty and Sort
	elif(item == '' and b1 and not b2 and not b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE price ORDER BY price ASC") 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#item is empty and Sort and 保固
	elif(item == '' and b1 and not b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (state_2 = '保固') AND price ORDER BY price ASC") 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#item is empty and Sort and 二手
	elif(item == '' and b1 and b2 and not b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE(state_1 = '二手') AND price ORDER BY price ASC") 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	# item is empty and general OUTPUT
	elif(item == '' and not b1 and not b2 and not b3):
		cmd = conn.execute("SELECT * FROM TASKS")
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1

	# Downward code for
	# item is not empty

	# Sort and 二手 and 保固
	elif (b1 and b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (sid LIKE ? AND state_1 = '二手' AND state_2 = '保固') AND price ORDER BY price ASC", ('%' + item + '%', )) 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#二手 and 保固		
	elif(not b1 and b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (sid LIKE ? AND state_1 = '二手' AND state_2 = '保固')", ('%' + item + '%', )) 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#保固
	elif(not b1 and not b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (sid LIKE ? AND state_2 = '保固')", ('%' + item + '%', )) 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#二手
	elif(not b1 and b2 and not b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE (sid LIKE ? AND state_1 = '二手')", ('%' + item + '%', )) 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#Soft
	elif(b1 and not b2 and not b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE sid LIKE ? AND price ORDER BY price ASC", ('%' + item + '%', )) 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#Soft and 保固
	elif(b1 and not b2 and b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE sid LIKE ? AND (state_2 = '保固') AND price ORDER BY price ASC", ('%' + item + '%', )) 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#Soft and 二手
	elif(b1 and b2 and not b3):
		cmd = conn.execute("SELECT * FROM TASKS WHERE sid LIKE ? AND (state_1 = '二手') AND price ORDER BY price ASC", ('%' + item + '%', )) 
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	#General OUTPUT
	else:
		cmd = conn.execute("SELECT * FROM TASKS WHERE sid LIKE ?", ('%' + item + '%', ))
		for row in cmd:
			data_list.append([row[0],str(row[1]),row[2],row[3],row[4],row[5]])
			count += 1
	return count, data_list

'''
void OpenWeb(String) :
	Open web
'''
def OpenWeb(url):
	webbrowser.open(url)

	
class App(QWidget):
	#Constructor
	def __init__(self):		
		super(self.__class__, self).__init__()
		
		#Init the main window
		self.setupUi()		
		self.show()	

	'''
	void setupUi(self, void) : 
		Initial the Layout
	'''
	def setupUi(self):
		self.setWindowTitle('web crawler')

		self.search_button = QPushButton('Search')
		self.search_label = QLabel('KeyWord')
		self.search_line = QLineEdit()
		self.sort_checkbox = QCheckBox('價格排序')
		self.state_checkbox = QCheckBox('二手用家')
		self.warranty_checkbox = QCheckBox('保固內')

		#Set Layout 
		form_layout = QFormLayout()			
		form_layout.addRow(self.search_label, self.search_line)
		form_layout.addRow(self.sort_checkbox, self.state_checkbox)
		form_layout.addRow(self.warranty_checkbox)
		form_layout.addRow(self.search_button)
		h_layout = QVBoxLayout()
		h_layout.addLayout(form_layout)
		self.setLayout(h_layout)
		
		#Signal and slot
		self.search_button.clicked.connect(self.search_click)

	'''
	void search_click(self, void) : 
		Act when the search_button clicked
	'''
	def search_click(self):
		item = self.search_line.text()
		page_num, ok = QInputDialog.getInt(self, "Search", "Enter a page number")
		if ok:
			WebCrawler(item, page_num)
			col, data_list = SelectDBData(item, self.sort_checkbox.isChecked(), self.state_checkbox.isChecked(), self.warranty_checkbox.isChecked())
			self.openDBWindow(data_list, col)
			self.hide()

	'''
	void openDBWindow(self, two_dimention_list) : 
		Show the final DataBase Windows to user
	'''
	def openDBWindow(self, data_list, col):
		url = ''
		db_window = QDialog(self)
		db_window.resize(1200, 400)
		my_table = QTableWidget(col, 6)
		horizontalHeader = ["SID","PRICE","LOCA","STATE1","STATE2", "ADDR"]
		for i in range(0 , col):
			for j in range(0, 6):
				newItem = QTableWidgetItem(data_list[i][j])
				my_table.setItem(i, j, newItem)
		my_table.setEditTriggers(QAbstractItemView.NoEditTriggers) 
		my_table.setSelectionBehavior(QAbstractItemView.SelectRows) 
		my_table.horizontalHeader()
		my_table.setHorizontalHeaderLabels(horizontalHeader)
		my_table.setColumnWidth(0, 200)
		my_table.setColumnWidth(1, 60)
		my_table.setColumnWidth(2, 200)
		my_table.setColumnWidth(3, 100)
		my_table.setColumnWidth(4, 100)
		my_table.setColumnWidth(5, 300)

		go_web_button = QPushButton('GO WEB')
		back_button = QPushButton('BACK')
		layout = QHBoxLayout()

		layout.addWidget(my_table)
		layout.addWidget(go_web_button)
		layout.addWidget(back_button)

		db_window.setLayout(layout)
		db_window.show()

		#Signal and slot
		go_web_button.clicked.connect(lambda:OpenWeb(my_table.currentItem().text()))
		back_button.clicked.connect(db_window.close)
		back_button.clicked.connect(self.show)

#---main---
if __name__ == '__main__':
	app = QApplication(sys.argv)
	conn = CreateDB()
	ex = App()
	sys.exit(app.exec_())

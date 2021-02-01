# -*- coding: utf-8 -*-
#imports scetion
import pandas as pdHandle
import urllib.request
import xml.etree.ElementTree as ETHandle
import tkinter as tkHandle

#static variables
window = tkHandle.Tk()
xlFileInput ='C:/Users/14632/input.csv'
xlFileRep1 = 'C:/Users/14632/report1.csv'
xlFileRep2 ='C:/Users/14632/report2.csv'
labelArray = ['Label1','Label2']  #Number of concerete products for factory
listBoxArray = ['ListBox1','ListBox2']
buttonArray = ['Report1Button','Report2Button']
addrList = []
crList = []
rep1ExpData = []
rep2ExpData = []

#Pattern 1: Facade Pattern
class ReportOne:
    def export(self):
        rep1ExpData = list(map(lambda x, y:(x,y), addrList,crList))
        df = pdHandle.DataFrame(rep1ExpData, columns=["Address", "Career Route"])
        df.to_csv(xlFileRep1, index = False)

class ReportTwo:
    def export(self):
        uniqueCRCount = []
        uniqueCRList = list(dict.fromkeys(crList))
        for crVal in crList: 
            uniqueCRCount.append(crList.count(crVal))
        rep2ExpData = list(map(lambda x, y:(x,y), uniqueCRList,uniqueCRCount))
        df = pdHandle.DataFrame(rep2ExpData, columns=["Career Route", "Count"])
        df.to_csv(xlFileRep2, index = False)

class GenerateReports:
    """Facade Pattern for generating report 1 and 2 on button clicks"""
    def __init__(self): 
        self.reportone = ReportOne() 
        self.reporttwo = ReportTwo()  
        
#Pattern 2: Factory 1
class Label(object):
   obj = ""
   def get_obj(self):
      return self.obj

class Label1(Label):
   obj = tkHandle.Label(window, text="1. Address and Career Route")

class Label2(Label):
   obj = tkHandle.Label(window, text="2. Career Route : Count")

class LabelFactory():
   def create_label(self, typ):
      return globals()[typ]()

#Pattern 3: Iterator Pattern
class RequestItem:
    def __init__(self, row):
        self.reqXML = """
<?xml version="1.0"?>
<AddressValidateRequest USERID="423UNIVE6333">
	<Revision>1</Revision>
	<Address ID="0">
    <Address1>"""+str(row[1])+' '+str(row[2])+"""</Address1>
		<Address2>"""+str(row[3])+"""</Address2>
		<City>"""+str(row[4])+"""</City>
		<State>"""+str(row[5])+"""</State>
		<Zip5>"""+str(row[6])+"""</Zip5>
		<Zip4/>
	</Address>
</AddressValidateRequest>
    """

    def __str__(self):
        return str(self.reqXML)

class RequestListIterator:
    def __init__(self, items):
        self.indx = 0
        self.items = items

    def has_next(self):
        return False if self.indx >= len(self.items) else True

    def next(self):
        item = self.items[self.indx]
        self.indx += 1
        return item

class RequestList:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def iterator(self):
        return RequestListIterator(self.items)
  
#Client code: We can also have this section completely separate
#Read Excel file and add to the iterator pattern
fileLines =pdHandle.read_csv(xlFileInput)
inputDataFrame = pdHandle.DataFrame(fileLines)
reqObj = RequestList() #Create Object for iterating 
for row in inputDataFrame.itertuples():
    rowEntry = RequestItem(row)
    reqObj.add(rowEntry) #Append to the list

iterator = reqObj.iterator()
while iterator.has_next():
        item = iterator.next()
        #Construct URL
        urlStr = str(item).replace('\n','').replace('\t','')
        urlStr = urllib.parse.quote_plus(urlStr)
        #One API to do both- autofill the address after validating and to determine the career route
        #API responses tested using the software ARC by Google Chrome, responses verified using USPS online portal
        url = "https://secure.shippingapis.com/ShippingAPI.dll?API=Verify&XML=" + urlStr
        #Send the GET request
        response = urllib.request.urlopen(url)
        if response.getcode() != 200:
            print("Error making HTTP call:")
            print(response.info())
            exit()    
            contents = response.read()
            print(contents)

        contents = response.read()
        root = ETHandle.fromstring(contents)
        for address in root.findall('Address'):
             #Construct address and route to be stored
             address1 = '' if address.find("Address1").text == 'NAN' else address.find("Address1").text+', '
             address2 = '' if address.find("Address2").text == 'NAN' else address.find("Address2").text+', '
             city = address.find("City").text + ', ' 
             state = address.find("State").text + ', ' 
             zipcode = address.find("Zip5").text
             addressTemp =  address1 + address2 + city + state + zipcode
             careerRouteTemp = address.find("CarrierRoute").text
             addrList.append(addressTemp)
             crList.append(careerRouteTemp)

#Pattern 2: Factory 2
class ListBox(object):
   obj = ""
   def get_obj(self):
       return self.obj

class ListBox1(ListBox):
   obj = tkHandle.Listbox(window, width=100)
   i = 1
   for xval, yval in zip(addrList, crList):
       obj.insert(i, 'Address: '+xval + ' and CareerRoute: ' +yval)
       i+=1
       print(xval, yval)

class ListBox2(ListBox):
   obj = tkHandle.Listbox(window, width=50)
   i = 1
   uniqueCRList = list(dict.fromkeys(crList))
   for crVal in uniqueCRList: 
       obj.insert(i, crVal + ' : ' +str(crList.count(crVal)))
       i+=1
    
class ListBoxFactory():
   def create_list(self, typ):
      return globals()[typ]()

genReport = GenerateReports()

#Pattern 2: Factory 3
class Button(object):
   obj = ""
   def get_obj(self):
      return self.obj

class Report1Button(Button):
   obj = tkHandle.Button(window, text="Export Report1", bg="Gray", command= genReport.reportone.export)

class Report2Button(Button):
   obj = tkHandle.Button(window, text="Export Report2", bg="Gray", command= genReport.reporttwo.export)

class ButtonFactory():
   def create_button(self, typ):
      return globals()[typ]()

#Create concrete factory objects
labelObj = LabelFactory()
listObj = ListBoxFactory()
buttonObj = ButtonFactory()

#List 1 displayed on the UI
lbl1 = labelObj.create_label(labelArray[0]).get_obj() 
lbl1.pack()
lst1 = listObj.create_list(listBoxArray[0]).get_obj() 
lst1.pack()
btn1 = buttonObj.create_button(buttonArray[0]).get_obj() 
btn1.pack()
   
#List 2 displayed in this order after list 1 on the UI
lbl2 = labelObj.create_label(labelArray[1]).get_obj() 
lbl2.pack()
lst2 = listObj.create_list(listBoxArray[1]).get_obj() 
lst2.pack()
btn2 = buttonObj.create_button(buttonArray[1]).get_obj() 
btn2.pack()

#GUI Details   
window.title("RouteMining App")
window.geometry('1000x700')   
window.mainloop()

import re
import PySimpleGUI as sg
import requests
from bs4 import BeautifulSoup
from proxy_checker import ProxyChecker
import concurrent.futures
import threading
import json


uncheckedProxies = []
table_content = []

def JSON_Convert(lists):
    JSON_Output = json.dumps(lists, separators=[",", ":"])
    with open('json_save.json', 'w') as output:
        output.write(JSON_Output)

def Text_Convert(proxies):
    with open("text_save.txt", "w") as output:
        for i in proxies:
            output.write(i + "\n")


        
# Function for scraping proxies from provided URLs
def proxyScraper():
    URLx = []   
    #Opens and reads users URL Addresses
    with open(values["-IMPORT-"], 'r') as f:
        URLList = f.readlines() 



    #Looping through the list of URLS provided.
    for ress in URLList:
        URLx.append(ress.strip())

    #Grabbing the HTML and parsing
    for res in URLx:
        html = requests.get(str(res))
        soup = BeautifulSoup(html.content, "html.parser")
        #Finding the proxies using regex
        prox = re.findall("[0-9]+(?:\.[0-9]+){3}:[0-9]+", str(soup))  
        #Looping through the found proxies. 
        for proxy in prox:
            #Checking if proxy exist. if not, appended.
            if proxy not in uncheckedProxies:
                uncheckedProxies.append(proxy)
    print("Proxies Scraped.")

#Initializing ProxyChecker
checker = ProxyChecker()

#Lists used to store values for the save functions
checked_Dict = []
proxies_list = []

def ProxyCheck(ip):
    # Using input IP and checking it with ProxyChecker
    groupAnswer = checker.check_proxy(ip)
    #Checking if there was a result
    if groupAnswer != False:
        #Appending to lists above; Used for the save functions
        proxies_list.append(ip)
        checked_Dict.append(groupAnswer)

        #Converting ProxyChecker result to a list; Needed
        # to output to UI table
        convert = []
        convert.append(ip)
        for i in groupAnswer.values():
            convert.append(i)
 
        #Appending new list to table content; This is the values argument pysimplegui table  
        table_content.append(convert)
        #Updating the table to the new table_content
        window["-TABLE-"].Update(values=table_content)


    
  
            
# Function for multithreading using concurrent.futures.ThreadPoolExecutor
def runThread():
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(workerCountInput)) as executor:
            #Running ProxyCheck funtion with the unchecked proxies as its argument
            executor.map(ProxyCheck, uncheckedProxies)
        
    except Exception:
        print("Proxy Checker initiation failed! Please check you have selected a thread count.")


# Right side of the UI: Start button, Thread input, Import Urls,
# Save buttons, Quality check checkbox
right_layout = [
        #Start Button
        [sg.Button("Start", visible=True)],
        #Import URLs Button
        [sg.FileBrowse("Import URLs", key="-IMPORT-")],
        #Thread count input
        [sg.Text("Thread Count:"),
        sg.Input(key="-THREAD-INPUT-", size=(5,5))],
        #Invisible button allowing usi
        #sg.Button("Sumbit", visible=False, bind_return_key=True)],

        [sg.Checkbox("Quality Check", default=True, change_submits=True, enable_events=True, key="-Checkbox-")],
        
        [sg.Button("Save as .txt", key="-SAVE-TEXT-")],
        [sg.Button("Save JSON", key="-SAVE-JSON-")]
]

layout = [[
    sg.Frame("Information Station", [[
    sg.Table(values = table_content,
    headings= ["IP:PORT", "PROTOCOL", "ANONYMITY", "TIMEOUT", "COUNTRY", "COUNTRY_CODE"],
    expand_x = True,
    key="-TABLE-"),
    sg.Column(right_layout, element_justification="center", expand_x=True),


    ]]),
    

]]

window = sg.Window("Basic Proxy Scraper", layout, finalize=True)
#window["-THREAD-INPUT-"].bind("<Return>", "_Enter")

while True:
    event, values = window.read()
    
    file_path = values["-IMPORT-"]
    workerCountInput = window["-THREAD-INPUT-"].get()
    

    if event == "Start":
        proxyScraper()
        # Checking if user wants proxies checked. If so, threads start
        if values["-Checkbox-"] == True: 
            # Using threading to run the runThread function;
            # Needed to avoid running on the main thread; pysimplegui issue.
            threading.Thread(target=runThread, daemon=True).start()

    # If save json button clicked, saves as .json file using
    # JSON_convert() function
    if event == "-SAVE-JSON-":
        JSON_Convert(checked_Dict)
    # If save txt button clicked, saves as .txt file using
    # Text_convert() function
    if event == "-SAVE-TEXT-":
        Text_Convert(proxies_list)
  

    if event == sg.WIN_CLOSED:
        break

       

       

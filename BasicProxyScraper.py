import re
import PySimpleGUI as sg
import requests
from bs4 import BeautifulSoup
from proxy_checker import ProxyChecker
import concurrent.futures
import threading

uncheckedProxies = []
table_content = []

def proxyScraper():
    URLx = []   
    #Opens and reads users URL Addresses
    with open(values["-IMPORT-"], 'r') as f:
        URLList = f.readlines() 



    #Starts looping through the list of URLS provided; Grabbing the HTML, parsing, and then searching for proxies.
    for ress in URLList:
        URLx.append(ress.strip())

    for res in URLx:
        html = requests.get(str(res))
        soup = BeautifulSoup(html.content, "html.parser")
        results = str(soup)
        prox = re.findall("[0-9]+(?:\.[0-9]+){3}:[0-9]+", results)  
        #Starts looping through the found proxies, checking if they already exist on the Users saved list and if not, adding it.
        for proxy in prox:
            if proxy not in uncheckedProxies:
                uncheckedProxies.append(proxy)
    print("URLS Grabbed")


checker = ProxyChecker()

def ProxyCheck(ip):
    # Using input IP and checking it with proxy-checker
    groupAnswer = checker.check_proxy(ip)

    if groupAnswer != False:

        print(groupAnswer)
        print(threading.active_count())
        convert = []


        print(groupAnswer.values())
        #AllProxies.append(ip)
        convert.append(ip)
        for i in groupAnswer.values():
 
            convert.append(i)
 

        table_content.append(convert)
        window["-TABLE-"].Update(values=table_content)


    
  
            
# Function for multithreading using concurrent.futures.ThreadPoolExecutor
def runThread():

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(workerCountInput)) as executor:
            executor.map(ProxyCheck, uncheckedProxies)
        
    except Exception:
        print("Thread Timed Out")


right_layout = [
        [sg.Button("Start", visible=True)],
        [sg.FileBrowse("Import URLs", key="-IMPORT-")],

        [sg.Text("Thread Count:"),
        sg.Input(key="-THREAD-INPUT-", size=(5,5)),
        sg.Button("Sumbit", visible=False, bind_return_key=True)],

        [sg.Checkbox("Quality Check", default=True, change_submits=True, enable_events=True, key="-Checkbox-")],
        
        [sg.Button("Save Proxies", key="-SAVE-")]
]

layout = [[
    sg.Frame("Information Station", [[
    sg.Table(values = table_content,
    headings= ["IP:PORT", "PROTOCOL", "ANONYMITY", "TIMEOUT", "COUNTRY", "COUNTRY_CODE"],
    expand_x = True,
    key="-TABLE-"),
    sg.Column(right_layout, element_justification="center", expand_x=True),


    ]]),
    
    #sg.Multiline(key="-TEXTBOX-", size=(30,10))
]]

window = sg.Window("Basic Proxy Scraper", layout, finalize=True)
window["-THREAD-INPUT-"].bind("<Return>", "_Enter")

while True:
    event, values = window.read()
    
    file_path = values["-IMPORT-"]
    workerCountInput = window["-THREAD-INPUT-"].get()
    

    if event == "Start":
        proxyScraper()
        # Checking if user wants proxies checked. If so, threads start
        if values["-Checkbox-"] == True: 
            threading.Thread(target=runThread, daemon=True).start()

    if event == sg.WIN_CLOSED:
        break

       

       

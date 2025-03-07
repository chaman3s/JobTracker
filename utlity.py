from handlingFile import handleFile
from bs4 import BeautifulSoup
import json
import re
import datetime
import os
import requests
import socket
from dotenv import load_dotenv
class utlity:
    def __init__(self):
        load_dotenv()
        self.db = handleFile()
        self.hun_api_key = os.getenv("api_Key")
    def dataprepared(self,com,ro,sk,jd,lk):
        print(com, ro, jd,sk )
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        data={}
        ct =self.find_company_emails(com)
        data[com] = {
                "role": ro,
                "skill": sk,
                "applied_time": timestamp,
                "link": lk,
                "hrContactDetails": ct,
                "job_description": jd,
                "status": "upload"
            }
            
        print(data)
        choice=input("data are correct(y/n)").lower()
        if choice == "y":
            return data
        elif choice == "n":
            data = self.dataEditor(data,com)
            return data
        else:
            print("Unknown choice!\n denied to save data")
            return True
        
    def checkCompany(self, company ,rtn=None ,pr=None):
        print("ok20")
        data = self.db.load_json()
        print("ok21")
        if company in data :
            if rtn is not None:
                return [True ,data[company]]
            else:
                print(f"Already applied on {data[company]['applied_time']}")
                return True
        
        else:return False
    def htmltotext(self, text):
        print("ok9")
        soup = BeautifulSoup(text, 'html.parser')
        print("ok10")
        g =soup.get_text(separator="\n", strip=True)
        print("ok11")
        return g
    def extract_json_from_props(self, response_text):
        start_index = response_text.find('{"props"')
        if start_index == -1:
            return None  

        brace_count = 0
        end_index = start_index
        for i, char in enumerate(response_text[start_index:], start=start_index):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_index = i + 1  
                    break

        return response_text[start_index:end_index]
    def dataEditor(self, dt,companyname,tim=None ,byd=None):
        while True:
            if byd==None:
                check = input("""which field do you want to edit?
                          c for comapny name 
                          j for job description
                          s for skills
                          r for role
                          h for hr contect details
                          st for change status
                          b for exit
                          """).lower()
            else:
                check= byd
            if check =="c":
                value = input ("enter  comanyname:")
                data =  {}
                data[value] =dt[companyname]
                dt = data
            elif check =="j":
                print("Enter Job Description (Type 'END' on a new line to finish):")
                jd_lines = []
                while True:
                    line = input()
                    if line.strip().upper() == "END":
                        break
                    jd_lines.append(line)
                    job_description = "\n".join(jd_lines)
                dt[companyname]["job_description"] = job_description
            elif check == "s":
                value = input ("enter  skill:")
                dt[companyname]["skill"] = value
            elif check == "r":
                value = input ("enter  role:")
                dt[companyname]["role"] = value
            elif check == "h":
                while True:
                    value = input ("enter  hr contect detail and b for back:")
                    if value.lower()=="b":
                        break
                    elif self.verify_email(value): 
                        pos=input("Please pls enter position:")
                        dt[companyname]["hrContactDetails"] = {pos:value}
                    
                    else:
                        print("""enter email is invaild or not pesent
                                 !pls try again with vaild email""")
            elif check == "st":
                value = input ("enter  status:")
                dt[companyname]["status"] = value
            elif check == "b":
                break
            
            else:
                print ("Invalid input ! try agian")
            if tim is not None:
                ch=input("did you  sent an email  mail? (y/n)").lower()
                if ch == "y":
                    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    dt[companyname]["applied_time"] = timestamp
                    dt[companyname]["status"] = "applied"
            if byd != None:
                break
                
        return dt

    def is_experience_above_one(self,text):
        match = re.search(r'(\d+)\s*-\s*(\d+)\s*years?', text,re.IGNORECASE)
        if match:
            years = int(match.group(1))
            return [years >=1,years]
        return[ False]


 # Replace with your valid Hunter.io API key

    def domain_exists(self,domain):
        """
        Check if a domain exists by attempting DNS resolution.
        Returns True if the domain resolves, False otherwise.
        """
        try:
            socket.gethostbyname(domain)
            return True
        except socket.error:
            return False

    def verify_domain_with_hunter(self,domain):
    
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.hun_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("data", {}).get("emails"):
                print(f"✅ Hunter.io found email records for domain: {domain}")
                return True
            else:
                print(f"❌ No email records found for domain: {domain}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error verifying domain {domain} via Hunter: {e}")
            return False

    def verify_email(self,email):
        url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={self.hun_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("status") == "valid"
        except requests.exceptions.RequestException as e:
            print(f"Error verifying email {email}: {e}")
            return False

    def find_company_emails(self,company_name, tlds=None):
    
        if tlds is None:
            tlds = [".com", ".in", ".net", ".org"]  # Add more TLDs if needed

        valid_domains = []
        for tld in tlds:
            try:
                domain = company_name.lower().replace(" ", "") + tld
                print(f"\nChecking domain: {domain}")
            except:
                break
            

            # Check if the domain resolves via DNS.
            if not self.domain_exists(domain):
                print(f"❌ Domain does not resolve: {domain}")
                continue

            # Then, check if Hunter.io has any email records for the domain.
            if self.verify_domain_with_hunter(domain):
                valid_domains.append(domain)

        if not valid_domains:
            print(f"\n❌ No valid domains with email records found for {company_name}.")
            valid_domains[0]= input("pls Enter domain name: ")

        # Search for emails using Hunter.io for each valid domain.
        emails_data = []
        for domain in valid_domains:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.hun_api_key}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                emails = data.get("data", {}).get("emails", [])
                for email_info in emails:
                    # Save both email and its associated position (if available)
                    record = {
                        "email": email_info.get("value"),
                        "position": email_info.get("position", "N/A")
                    }
                    emails_data.append(record)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching emails for {domain}: {e}")
                continue
        if not emails_data:
            return "ny"
        return emails_data


  

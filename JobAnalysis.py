import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import datetime
from utlity import utlity


class Jobanalysis:
    def __init__(self):
        self.results = ""
        self.job_links = ""
        self.ut = utlity()
       
        
    def process_job(self):
        parsed_url = urlparse(self.job_links)
        domain_name = parsed_url.netloc
        print(domain_name) 
        if domain_name == "www.linkedin.com":
           return self.linkedinJobAdder()
        elif domain_name == "www.expertia.ai":
            return self.expertiaJobadder()
        elif domain_name == "www.timesjobs.com":
            return self.timesjobsJobAdder()
        elif domain_name == "cutshort.io":
            return self.cutshortJobAdder()
        else:
            print ("Unknown domain")
            return True

    def expertiaJobadder(self):
        json_text = self.ut.extract_json_from_props(self.results)
        if not json_text:
            return None
        
        try:
            job_text = json.loads(json_text)["props"]["pageProps"]['jobDetails']
        except Exception as e:
            print("Error parsing JSON:", e)
            return None

        company_name = job_text.get('company_full_name', 'Not Found')
        role = job_text.get('role', 'Not Found')
        skills = ",".join([skill["skill"] for skill in job_text.get("skills", [])])
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        hrContactDetails= re.findall(email_pattern, self.results)

        jd = self.ut.htmltotext(job_text.get("job_desc", ""))
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        data={}
        data[company_name] = {
                "role": role,
                "skill": skills,
                "applied_time": timestamp,
                "link": self.job_links,
                "hrContactDetails": hrContactDetails,
                "job_description": jd,
                "status": "upload"
            }

        print("Application added successfully!")
        return True

    def linkedinJobAdder(self):
        print("ok4")
        if "jobs/view" in self.job_links:
            print("ok5")
            return self.linkdeinJobAnalyst() 
        elif "posts" in self.job_links:
            return self.linkdeinPostAnalyst()
        else:
            return "Unknown"

    def linkdeinJobAnalyst(self):
        print("ok6")
        lines = self.ut.htmltotext(self.results).split("\n")
        print("ok7")

    # Extracting lines containing "hiring"
        print("ok12")
        hiring_lines = [line for line in lines if "hiring" in line.lower()]
        print("ok13")

    # Check if there are any matching lines
    
        if hiring_lines:
            text = hiring_lines[0]  # First line with "hiring"
            print("ok14")
        # Use regex to extract company name and role safely
            match = re.search(r"(.*?) hiring (.*?) in", text, re.IGNORECASE)
            print("ok15")
            if match:
                print("ok16")
                company_name = match.group(1).strip()
                print("ok17")
                check = self.ut.checkCompany(company_name)
                print("ok18")
                if check:
                    return True
                print("ok19")
                role = match.group(2).strip()
            else:
                company_name = "Unknown"
                role = "Unknown"

        # Convert lines list into a single string for splitting
            full_text = "\n".join(lines)
            print(full_text)

        # Extract job description safely
            if ("Job Summary" in full_text or "Job Description" in full_text) and "Show more" in full_text:
                try:
                    job_desc = full_text.split("Job Summary")[1].split("Show more")[0]
                except IndexError:
                    try:
                        job_desc = full_text.split("Job Description")[1].split("Show more")[0]
                    except IndexError:
                        job_desc = "Job description not found"
            elif("About Persistent" in full_text)and "Show more" in full_text:
                try:
                    job_desc = full_text.split("About Persistent")[1].split("Show more")[0]
                except IndexError:
                     job_desc = "Job description not found"
            elif("Responsibilities" in full_text)and "Show more" in full_text:
                try:
                    job_desc = full_text.split("Responsibilities")[1].split("Show more")[0]
                except IndexError:
                     job_desc = "Job description not found"
            
            else:
                job_desc = "Job description function have problem"
            year = self.ut.is_experience_above_one(job_desc)
            if year[0]:
                print(f"This  job  requires {year[1]} years of experience")
                return True
            
            if ("Skills" in full_text  in full_text) and "Show more" in full_text:
                try:
                    skill = full_text.split("Skills")[1].split("Show more")[0]
                except IndexError:
                    try:
                        skill= full_text.split("Skills")[1].split("Show more")[0]
                    except IndexError:
                        skill= "Job description not found"
            else:
                skill = "Skills function have problem"

            print(company_name, role, job_desc,skill )
            timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            data={}
            data[company_name] = {
                "role": role,
                "skill": skill,
                "applied_time": timestamp,
                "link": self.job_links,
                "hrContactDetails": "ny",
                "job_description": job_desc,
                "status": "upload"
            }
            
            print(data)
            choice=input("data are correct(y/n)").lower()
            if choice == "y":
                return data
            elif choice == "n":
                data = self.ut.dataEditor(data,company_name)
                return data
            else:
                return True
        else:
            print("No hiring-related lines found")
            return None
    
    def linkdeinPostAnalyst(self):
        return self.ut.htmltotext(self.results)
    def timesjobsJobAdder(self):
        print(self.ut.htmltotext(self.results))
    def cutshortJobAdder(self):
        lines= self.ut.htmltotext(self.results)
        print(lines)
        hiring_lines = [line for line in lines if "hiring" in line.lower()]
        print(hiring_lines)

        

import os
import json
import datetime
import re
import requests  # Make sure you have this installed: pip install requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from JobAnalysis import Jobanalysis
from handlingFile import handleFile
from utlity import utlity
class JobTracker:
    def __init__(self):
        self.ja= Jobanalysis()
        self.db = handleFile()
        self.ut = utlity()
    def add_application(self):
        """Add a new job application to the database."""
        restart = False
        reset = False
        while True:
            company = input("Enter company name (or type 'b' to go back to Main menu): ").strip()
            if company.lower() == "b":
                break

            if self.ut.checkCompany(company):
                continue  # Skip duplicate entry

            # Collect remaining details manually
            while True:
                reset = False
                restart = False
                role = input("Enter role: ").strip()
                if role == "^D":
                    restart = True
                    break
                if role == "^B":
                    print("going back")
                    reset = True
                    break

                while True:
                    restart = False
                    reset = False
                    skill = input("Enter skill: ").strip()
                    if skill == "^D":
                        restart = True
                        break
                    if skill == "^B":
                        print("going back")
                        reset = True
                        break

                    while True:
                        restart = False
                        reset = True
                        link = input("Enter link: ").strip()
                        if link == "^D":
                            restart = True
                            break
                        if link == "^B":
                            print("going back")
                            reset = True
                            break

                        while True:
                            restart = False
                            reset = False
                            hrContactDetails = input("Enter HR contact details: ").strip()
                            if hrContactDetails == "^D":
                                restart = True
                                break
                            if hrContactDetails == "^B":
                                print("going back")
                                reset = True
                                break
                            print("Enter Job Description (Type 'END' on a new line to finish):")
                            jd_lines = []
                            restart = False
                            reset = False
                            while True:
                                line = input()
                                if line == "^D":
                                    restart = True
                                    break
                                if line == "^B":
                                    print("going back")
                                    reset = True
                                    break
                                if line.strip().upper() == "END":
                                    break
                                jd_lines.append(line)
                                job_description = "\n".join(jd_lines)
                            if reset:
                                reset = False
                                continue
                            break
                        if reset:
                            reset = False
                            continue
                        break
                    if reset:
                        reset = False
                        continue
                    break
                if reset:
                    reset = False
                    continue
                break
            if reset or restart:
                reset = False
                restart = False
                continue

            timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Correct format
            data = {}
            
            data[company] = {
                "role": role,
                "skill": skill,
                "applied_time": timestamp,
                "link": link,
                "hrContactDetails": hrContactDetails,
                "job_description": job_description,
                "status": "upload"
            }

            self.db.save_json(data)
            print("Application added successfully!")

    def edit_application(self):
        """Edit a particular company's application details."""
     
        company = input("Enter company name to edit: ").strip()
        
        data= self.ut.checkCompany(company,rtn=True)
        if data[0] :
            print("Company not found!")
            return
        print(f"Editing details for {company}:")
        da= {}
        da[company ]=data[1]
        da=self.ut.dataEditor(da)
        self.db.save_json(da)
        print("Application updated successfully!")

    def delete_application(self,com = None):
        """Delete a company from the database."""
       
        data = self.db.load_json()
        if com is None:
            com = input("Enter company name to delete: ").strip()
        if com not in data:
            print("Company not found!")
            return

        del data[com]
        self.db.save_json(data,com)
        print(f"Application for {com} deleted successfully!")

    def search_similar_companies(self, search_term):
        """Find similar company names."""
        data = self.db.load_json()
        search_term = search_term.lower()
        return [comp for comp in data if search_term in comp.lower()]

    def update_status(self):
        """Update the status of an application."""
        data = self.db.load_json()

        search_term = input("Enter company name to update status: ").strip()
        similar_companies = self.search_similar_companies(search_term)

        if not similar_companies:
            print("No matching companies found.")
            return

        print("\nMatching Companies:")
        for idx, company in enumerate(similar_companies, start=1):
            print(f"{idx}. {company}")

        while True:
            try:
                choice = int(input("Enter number to select a company: "))
                if 1 <= choice <= len(similar_companies):
                    selected_company = similar_companies[choice - 1]
                    break
                else:
                    print("Invalid selection, try again.")
            except ValueError:
                print("Invalid input, enter a number.")

        while True:
            status = input("Enter 'i' for Interview, 'r' for Rejected, or 'a' for Applied: ").strip().lower()
            if status in ["i", "r", "a"]:
                data[selected_company]["status"] = (
                    "interview"  if status == "i" else "applied" if status == "a" else "rejected"
                )
                self.db.save_json(data,selected_company)
                print(f"Status updated to '{data[selected_company]['status']}' for {selected_company}.")
                break
            else:
                print("Invalid input. Enter 'i', 'r', or 'a'.")

    def parse_date(self, date_str):
        """Try parsing the date in multiple formats."""
        for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                pass
        raise ValueError(f"Unknown date format: {date_str}")

    def categorize_past_applications(self):
        inp = True
        while True:
            """Print categorized job applications and allow selection to view details."""
            data = self.db.load_json()
            print(data ,"okd\n")
            today = datetime.datetime.now()
            time_frames = {
                "Today": today,
                "3 Days Ago": today - datetime.timedelta(days=3),
                "7 Days Ago": today - datetime.timedelta(days=7),
                "15 Days Ago": today - datetime.timedelta(days=15),
                "30+ Days Ago": today - datetime.timedelta(days=30)
            }

            categorized_companies = []
            index_mapping = {}

            print("\n=== Categorized Applications ===")
            index = 1
            for category, date_threshold in time_frames.items():
                category_list = [
                    (comp, details) for comp, details in data.items()
                    if details["status"] == "applied" and 
                    self.parse_date(details["applied_time"]) == date_threshold.date()
                ]
                if category_list:
                    print(f"\n{category}:")
                    for company, _ in category_list:
                        print(f"{index}. {company}")
                        index_mapping[str(index)] = company
                        categorized_companies.append(company)
                        index += 1
            upload_pending_list = [
                (comp, details) for comp, details in data.items()
                if details["status"] == "upload"
            ]

            if upload_pending_list:
                print("\nNot Applied yet:")
            for company, _ in upload_pending_list:
                print(f"{index}. {company}")
                index_mapping[str(index)] = company
                categorized_companies.append(company)
                index += 1

            if not categorized_companies:
                print("\nNo active applications found.")
            if inp:
                choice = input("\nEnter a number to view details (or press 'b' to go back): ").strip()
            if choice.lower() == "b":
                break
            
            elif choice in index_mapping:
                company = index_mapping[choice]
                print(f"\nDetails for {company}:")
                for key, value in data[company].items():
                    print(f"{key}: {value}")
                while True:
                    imp = True
                    i = input("""u for update status b for back  d for delete:""").lower()
                    if i == "b":
                        break
                    elif i == "u":
                        if data[company]["status"] == "upload":
                            dta =self.ut.dataEditor(data,company,tim=True)
                        else :
                            dta =self.ut.dataEditor(data,company,tim=False)
                        self.db.save_json(dta,company)
                    elif i == "d":
                        self.delete_application(company)
                        inp=False
                        break
                    else:
                        print("Invalid input try agian")
            else:
                print("Invalid choice, try again.")
    def extract_json_from_props(self,response_text):
    # Find the starting index of the JSON block that begins with '{"props"'
        start_index = response_text.find('{"props"')
        if start_index == -1:
            return None  # Not found

        # Use a counter to track the nesting of braces.
        brace_count = 0
        end_index = start_index
        for i, char in enumerate(response_text[start_index:], start=start_index):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_index = i + 1  # Include the closing brace
                    break

        # Return the extracted JSON text.
        return response_text[start_index:end_index]
    def analyze_job_post(self):
         while True:
            job_link = input("enter url or text or enter e for exit:").strip()
            if job_link =="e":
                break
            if job_link.startswith("http://") or job_link.startswith("https://"):
                try:
                    i=3
                    response = requests.get(job_link)
                    print("ok")
                    if response.status_code == 200:
                        print("ok1")
                        self.ja.results =response.text
                        print("ok2")
                        self.ja.job_links= job_link
                        
                        print(f"ok{i}")
                        i+=1
                    
                        data =self.ja.process_job()
                        print(f"ok{i}")
                        i+=1
                        
                        if data==True:
                            continue 
                        elif data==None:
                            print("automatic given error")
                            self.add_application()
                        elif isinstance(data, list):
                            for j in data:
                                print(f"ok{1}:",j)
                                self.db.save_json(j)
                        else:
                            print(f"ok{i}")
                            i+=1
                            self.db.save_json(data)
                        
                except Exception as e:
                    print("Error fetching the link:", e)
                    return
       
db = JobTracker()
# choice = "8"
while True:
    print("\nOptions:")
    print("1. Add new application")
    print("2. Edit application")
    print("3. Delete application")
    print("4. Search for a company")
    print("5. Update application status")
    print("6. Show categorized past applications")
    print("7. Exit")
    print("8. Analyze job post text/link")

    choice = input("Enter your choice: ").strip()
   

    if choice == "1":
        db.add_application()
    elif choice == "2":
        db.edit_application()
    elif choice == "3":
        db.delete_application()
    elif choice == "4":
        search = input("Enter company name to search: ").strip()
        results = db.search_similar_companies(search)
        if results:
            print("Matching companies:", ", ".join(results))
        else:
            print("No matching companies found.")
    elif choice == "5":
        db.update_status()
    elif choice == "6":
        db.categorize_past_applications()
    elif choice == "7":
        print("Bye bye")
        break
    elif choice == "8":
        db.analyze_job_post()
        # choice="7"
    else:
        print("Invalid choice, try again!")

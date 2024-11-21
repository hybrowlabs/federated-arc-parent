import json
import frappe
import requests


#Background Job For Master Creation In Federated Instance
def master_doctype_creation():
    sites=frappe.get_all("Site",{"status":"Live"},["name"])
    for si in sites:
        site=frappe.get_doc("Site",si.name)
        master_list=frappe.get_doc("Site Federation Config")
        master= [mas_doc.select_doctype for mas_doc in master_list.master_doctypes]
        url=f'{site.site_name}/api/method/federation_child.api.get_master_list'
        api_secret =site.get_password(fieldname="api_secret_pass", raise_exception=False)
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'token '+str(site.api_key)+":"+str(api_secret)
        }
        response = requests.request("GET", url, headers=headers)
        if response.json().get("message"):
            for mas in response.json().get("message"):
                if mas not in master:
                    if not frappe.db.exist("DocType",mas):
                        url=f'{site.site_name}/api/method/federation_child.api.get_doctype_schema'
                        payload=json.dumps({
                            "doctype":mas
                        })
                        headers = {
                            'Content-Type': 'application/json',
                            'Authorization':'token '+str(site.api_key)+":"+str(api_secret)
                        }
                        response = requests.request("GET", url, headers=headers,data=payload)
                        if response.json().get("message"):
                            doc=frappe.get_doc(response.json().get("message"))
                            doc.insert()
                            master_list.append("master_doctypes",{
                                "select_doctype":doc.name

                            })
                            master_list.save(ignore_permissions=True)
                    else:
                        master_list.append("master_doctypes",{
                            "select_doctype":doc.name

                        })
                        master_list.save(ignore_permissions=True)


                




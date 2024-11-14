import json
import frappe
import requests


#get_api secret Api
@frappe.whitelist(allow_guest=True)
def get_api_secret():
    """
    Generate api Key Secret
    """
    user = frappe.get_doc('User', "Administrator")
    api_secret = user.get_password('api_secret') if user.api_secret else None
    if not user.api_key:
        api_key = frappe.generate_hash(length=15)
        user.api_key = api_key
        user.save(ignore_permissions=True)
    if not api_secret:
        api_secret = frappe.generate_hash(length=15)
        user.api_secret = api_secret
        user.save(ignore_permissions=True)
    return str(user.api_key),str(user.api_secret)



@frappe.whitelist()
def create_site(site_name,api_key,api_secret):
    """
    Create Site API
    """
    doc=frappe.new_doc("Erpnext Site")
    doc.site_name=site_name
    doc.api_key=api_key
    doc.api_secret_pass=api_secret
    doc.save(ignore_permissions=True)

#Get Master List Api
@frappe.whitelist()
def get_master_list():
    master=frappe.get_doc("Master List")
    master_list= [mas_doc.select_doctype for mas_doc in master.master_doctypes]
    return master_list



#Create Master Doctype Record
@frappe.whitelist()
def create_master_records(doctype,data,docnames):
    records=[]
    for rec in eval(docnames):
        record=frappe.get_doc(doctype,rec)

        records.append(record.as_dict())
    for site in json.loads(data):
        doc=frappe.get_doc("Erpnext Site",site.get("site"))
        api_secret =doc.get_password(fieldname="api_secret_pass", raise_exception=False)

        url=f'{site.get("site")}/api/method/federation_child.api.create_master_record'
        payload=json.dumps({
            "records":records
        },default=str)
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'token '+str(doc.api_key)+":"+str(api_secret)
        }
        response = requests.request("POST", url, headers=headers,data=payload)
        if response.status_code==200:
            log=frappe.new_doc("Sync Log")
            log.doctype_name=doctype
            log.site_name=site.get("site")
            log.status="Completed"
            for rec in eval(docnames):
                log.append("sync_records",{
                    "record":rec,
                    "doctype_name":doctype
                })
            log.save(ignore_permissions=True)
            frappe.msgprint("Documents Created Sucessfully")
        else:
            log=frappe.new_doc("Sync Log")
            log.doctype_name=doctype
            log.site_name=site.get("site")
            log.status="Failed"
            for rec in eval(docnames):
                log.append("sync_records",{
                    "record":rec,
                    "doctype_name":doctype
                })
            log.error=response.text
            log.save(ignore_permissions=True)
            frappe.msgprint("Document Not Pushed. Check sync log for more details")


#create company related documents in child
@frappe.whitelist()
def create_company_related_documents(company):
    records={}
    accounts=frappe.db.get_all("Account",{'company':company},["*"])
    cost_center=frappe.db.get_all("Cost Center",{'company':company},["*"])
    warehouse=frappe.db.get_all("Warehouse",{'company':company},["*"])
    department=frappe.db.get_all("Department",{'company':company},["*"])
    records.update({"cost_center":cost_center,"accounts":accounts,"warehouse":warehouse,"department":department})
    return records
                


#Create document change request Api child to fedaration
@frappe.whitelist()
def create_document_change_request(name,ref_doctype,status,docname,data,new_data,erpnext_site):
    doc=frappe.new_doc("Document Change Request")
    doc.ref_doctype=ref_doctype
    doc.status=status
    doc.docname=docname
    doc.data=data
    doc.new_data=new_data
    doc.erpnext_site=erpnext_site
    doc.save(ignore_permissions=True)
    frappe.db.set_value("Document Change Request",doc.name,"name",name)
    frappe.db.commit()

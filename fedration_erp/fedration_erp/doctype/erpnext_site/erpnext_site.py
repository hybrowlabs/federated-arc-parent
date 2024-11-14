# Copyright (c) 2024, ajay@mail.hybrowlabs.com and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
import requests


class ErpnextSite(Document):
	def before_save(self):
		self.master_doctype_creation()

	#Master list filters
	@frappe.whitelist()
	def get_master_list(self):
		master_list=frappe.db.get_all("Master Doctypes",{"parent":"Master List"},pluck="select_doctype")
		return master_list
	

	#Append Template Doctypes
	@frappe.whitelist()
	def get_master_template_values(self,mt):
		master_list=frappe.db.get_all("Master Doctypes",{"parent":mt},pluck="select_doctype")
		return master_list


	#Master Doctype Creation Federated Child To Master
	def master_doctype_creation(self):
		if self.status=="Live":
			master=self.get_master_list()
			url=f'{self.site_name}/api/method/federation_child.api.get_master_list'
			api_secret =self.get_password(fieldname="api_secret_pass", raise_exception=False)
			headers = {
				'Content-Type': 'application/json',
				'Authorization':'token '+str(self.api_key)+":"+str(api_secret)
			}
			response = requests.request("GET", url, headers=headers)
			if response.json().get("message"):
				for mas in response.json().get("message"):
					if mas not in master:
						url=f'{self.site_name}/api/method/federation_child.api.get_doctype_schema'
						payload=json.dumps({
							"doctype":mas
						})
						headers = {
							'Content-Type': 'application/json',
							'Authorization':'token '+str(self.api_key)+":"+str(api_secret)
						}
						response = requests.request("GET", url, headers=headers,data=payload)
						if response.json().get("message"):
							doc=frappe.get_doc(response.json().get("message"))
							doc.insert()
							master=frappe.get_doc("Master List")
							master.append("master_doctypes",{
								"select_doctype":doc.name

							})
							master.save(ignore_permissions=True)
				


# Copyright (c) 2024, ajay@mail.hybrowlabs.com and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
import requests

class SyncLog(Document):
	@frappe.whitelist()
	def get_master_record(self):
		records=[]
		for rec in self.sync_records:
			doc=frappe.get_doc(rec.doctype_name,rec.record)
			records.append(doc.as_dict())
		
		doc=frappe.get_doc("Federated Site",self.site_name)
		api_secret =doc.get_password(fieldname="api_secret_pass", raise_exception=False)

		url=f'{self.site_name}/api/method/federation_child.api.create_master_record'
		payload=json.dumps({
			"records":records
		},default=str)
		headers = {
			'Content-Type': 'application/json',
			'Authorization':'token '+str(doc.api_key)+":"+str(api_secret)
		}
		response = requests.request("POST", url, headers=headers,data=payload)
		if response.status_code==200:
			self.status="Completed"
			self.save(ignore_permissions=True)
		else:
			self.error=response.text
			self.save(ignore_permissions=True)
			frappe.db.commit()
			frappe.throw("Error")

			
			

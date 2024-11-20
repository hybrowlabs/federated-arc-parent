# Copyright (c) 2024, ajay@mail.hybrowlabs.com and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
import requests


class FederatedSite(Document):
	def before_save(self):
		self.master_doctype_creation()
		if self.get("__islocal"):
			self.create_oauth_client()

	#Master list filters
	@frappe.whitelist()
	def get_master_list(self):
		master_list=frappe.db.get_all("Master Doctypes",{"parent":"Site Federation Config"},pluck="select_doctype")
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
							master=frappe.get_doc("Site Federation Config")
							master.append("master_doctypes",{
								"select_doctype":doc.name

							})
							master.save(ignore_permissions=True)

	def create_oauth_client(self):
		oath_cli=frappe.db.get_value("OAuth Client",self.name,"name")
		if not oath_cli:
			doc=frappe.new_doc("OAuth Client")
			doc.app_name=self.site_name
			doc.skip_authorization=1
			doc.redirect_uris=str(self.site_name)+"/api/method/frappe.integrations.oauth2_logins.login_via_frappe"
			doc.default_redirect_uri=str(self.site_name)+"/api/method/frappe.integrations.oauth2_logins.login_via_frappe"
			doc.save(ignore_permissions=True)
			self.create_social_key_on_child(doc.client_id,doc.client_secret)
		else:
			doc=frappe.get_doc("OAuth Client",self.name)
			self.create_social_key_on_child(doc.client_id,doc.client_secret)
		


	def create_social_key_on_child(self,client_id,client_secret):
		url=f'{self.site_name}/api/method/federation_child.api.create_social_login'
		api_secret =self.get_password(fieldname="api_secret_pass", raise_exception=False)
		payload=json.dumps({
							"client_id":client_id,
							"client_secret":client_secret,
							"base_url":self.name
						})
		headers = {
			'Content-Type': 'application/json',
			'Authorization':'token '+str(self.api_key)+":"+str(api_secret)
		}
		response = requests.request("POST", url, headers=headers,data=payload)
		if response.status_code!=200:
			frappe.throw("Social Login Not Created")

				


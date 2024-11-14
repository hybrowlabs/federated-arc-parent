// Copyright (c) 2024, ajay@mail.hybrowlabs.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sync Log", {
	refresh(frm) {
    if(frm.doc.status=="Failed"){
        frm.add_custom_button(__('Retry'), function() {
            frappe.call({
                "method":"get_master_record",
                doc:frm.doc,
                callback:function(frm){
                    
                }
            })

        })
    }
	},
});

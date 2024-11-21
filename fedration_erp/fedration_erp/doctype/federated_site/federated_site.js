// Copyright (c) 2024, ajay@mail.hybrowlabs.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Federated Site", {
    refresh(frm){
        frappe.call({
            method:"get_master_list",
            doc:frm.doc,
            callback:function(r){
                if(r.message){
                    frm.set_query('select_doctype','sync_doctypes', (doc, cdt, cdn) => {
                        return {
                            filters: [
                                ['DocType', 'name', 'in', r.message]
                            ]
                        };
                    })
                }

            }
        })
    },
    master_template:function(frm){
        frappe.call({
            method:"get_master_template_values",
            doc:frm.doc,
            args:{
                mt:frm.doc.master_template
            },
            callback:function(r){
                frm.clear_table("sync_doctypes")
                if(r.message){
                    $.each(r.message,function(i,m){
                    let child = frm.add_child('sync_doctypes');
                    child.select_doctype=m
                    })
                    frm.refresh()
                }

            }
        })
    }
});


frappe.router.on('change', () => {
    addOCRMenuItem()
})



const addOCRMenuItem = async () => {
  frappe.call({
      method: 'fedration_erp.fedration_erp.api.get_master_list',
      callback: function(r) {
          const doctypes = r.message;
              if (doctypes.includes(frappe.get_route()[1])){
              cur_list?.page?.add_action_item(__('Push To Child Site'), function () {
                const docnames = get_checked_items(true);
                const dialog = new frappe.ui.Dialog({
                  title: __("Select Site"),
                  size: "large",
                  fields: [
                  {
                    fieldname: "sites",
                    fieldtype: "Table",
                    label: __("Sites"),
                    allow_bulk_edit: false,
                    data: [],
                    fields: [
                      {
                        fieldname: "site",
                        fieldtype: "Link",
                        label: __("ERPNext Site"),
                        options: "Federated Site",
                        reqd: 1,
                        in_list_view: 1,
                        // get_query: () => {
                        //   return {
                        //     query: "erpnext.controllers.queries.get_filtered_child_rows",
                        //     filters: {
                        //       parenttype: frm.doc.doctype,
                        //       parent: frm.doc.name,
                        //       reserve_stock: 1,
                        //     },
                        //   };
                        // },
                      },
                      
                    ],
                    
                  },
                ],
                primary_action_label: __("Push"),
                primary_action: () => {
                  var data = { items: dialog.fields_dict.sites.grid.data };
                  if (data.items && data.items.length > 0) {
                    if(frappe.get_route()[1]=="Company"){
                      frappe.call({
                        method: "fedration_erp.fedration_erp.api.create_master_records",
                        args: {
                          doctype:frappe.get_route()[1],
                          data: data.items,
                          docnames:docnames
                        },
                        freeze: true,
                        freeze_message: __("Creating Records On Sites..."),
                        callback: (r) => {
                        },
                      });
                    }
                    dialog.hide();
                  } else {
                    frappe.msgprint(__("Please select Sites"));
                  }
                },
                })
                dialog.show();
              });
            }
              
      }
  });
}


const get_checked_items=(only_docnames)=> {
  const docnames = Array.from(cur_list?.$checks || []).map((check) =>
    cstr(unescape($(check).data().name))
  );

  if (only_docnames) return docnames;

  return this.data.filter((d) => docnames.includes(d.name));
}
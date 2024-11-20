frappe.pages['fedrated-child'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Fedrated Child ',
		single_column: true
	});
	 // Fetch and display records
	 frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Federated Site',
            fields: ['name', 'site_name', 'status'], // Adjust fields as per your doctype
            limit_page_length: 20
        },
        callback: function (response) {
            const records = response.message;

            // Create HTML table with clickable rows
            const html = `
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Domain</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${records.map(record => `
                            <tr class="site-record" data-domain="${record.site_name}">
                                <td>${record.site_name}</td>
                                <td>${record.status}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;

            // Append to the page
            $(page.body).html(html);

            // Add click event for rows
            $('.site-record').on('click', function () {
                const domain = $(this).data('domain');
                // Generate login token and redirect
                frappe.call({
                    method: 'fedration_erp.fedration_erp.api.get_token',
                    args: {
                        domain:domain
                    },
                    callback: function (r) {
                        if (r.message) {
							const newTab = window.open(r.message, '_blank');
						} else {
							frappe.msgprint(__('Failed to retrieve session ID.'));
						}
					
                    }
                });
            });
        }
    });
}

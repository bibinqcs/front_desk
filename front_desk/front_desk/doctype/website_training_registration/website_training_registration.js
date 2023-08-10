// Copyright (c) 2023, Quark Cyber Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Website Training Registration', {
	refresh(frm) {
		frm.add_custom_button(__('Create Customer'), function(){
			frm.call('create_customer')
			    .then(r => {
			        if (r.message) {
						console.log("Works")
			        }
			});
		});
	}
});

// Copyright (c) 2020, Quark Cyber Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Suprema Biometric Device Integration', {
	manual_sync: function(frm) {
		if (frm.doc.from_date && frm.doc.to_date) {
			frappe.call({
				method: "front_desk.front_desk.doctype.suprema_biometric_device_integration.suprema_biometric_device_integration.api_manual_sync",
				args: {
					from_date: frm.doc.from_date,
					to_date: frm.doc.to_date
				},
				callback: function(r) {
					frappe.show_alert({
						message:__('Sync Successful'),
						indicator:'green'
					}, 5)
				}
			});
		} else {
			frappe.throw(__("Please enter both from date and to date"));
		}
	}
});

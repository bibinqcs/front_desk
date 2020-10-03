// Copyright (c) 2020, Quark Cyber Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Suprema Biometric Device Integration', {
	manual_sync: function(frm) {
		if (frm.doc.from_date && frm.doc.to_date && frm.doc.event_code) {
			if (frm.doc.event_code == "Fingerprint") {
				var code = "4865"
			} else {
				var code = "4102"
			}
			frappe.call({
				method: "front_desk.front_desk.doctype.suprema_biometric_device_integration.suprema_biometric_device_integration.api_manual_sync",
				args: {
					from_date: frm.doc.from_date,
					to_date: frm.doc.to_date,
					event_code: code
				},
				callback: function(r) {
					frappe.show_alert({
						message:__('Sync Successful'),
						indicator:'green'
					}, 5)
				}
			});
		} else {
			frappe.throw(__("Please enter both from date, to date and select type of authentication"));
		}
	},
	mark_attendance: function(frm) {
		if (frm.doc.att_from_date && frm.doc.att_to_date) {
			frappe.call({
				method: "front_desk.front_desk.doctype.suprema_biometric_device_integration.suprema_biometric_device_integration.mark_attendance",
				args: {
					att_from_date: frm.doc.att_from_date,
					att_to_date: frm.doc.att_to_date
				},
				callback: function(r) {
					frappe.show_alert({
						message:__('Attendance Marked'),
						indicator:'green'
					}, 5)
				}
			});
		} else {
			frappe.throw(__("Please enter both from date and to date"));
		}
	}
	
});

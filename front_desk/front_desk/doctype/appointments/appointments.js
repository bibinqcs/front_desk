// Copyright (c) 2017, Quark Cyber Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Appointments', {
	refresh: function(frm) {

	if(frm.doc.type=="Observation / Assessment"){
		frm.add_custom_button(__("Register to Waiting List"), function() {
			 frappe.model.open_mapped_doc({
				 method: "front_desk.front_desk.doctype.appointments.appointments.register_student",
				 frm: cur_frm
			 });
			}, __("Make"));
	 }		

	}
});

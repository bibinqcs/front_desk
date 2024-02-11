// Copyright (c) 2023, Quark Cyber Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Online Client Registration', {
//	refresh: function(frm) {
//		frm.add_custom_button(__("Add Guardians"), function() {
//			return frappe.call({
//				method: "front_desk.front_desk.doctype.online_student_registration.online_student_registration.add_guardians",
//				args: {
//					waitinglist: frm.doc.name,
//				},
//				callback: (r) => {
//					frm.refresh_field("guardians")
//				},
//			});
//		}, __("Make"));
//		frm.add_custom_button(__("Register Student"), function() {
//			frappe.model.open_mapped_doc({
//				method: "front_desk.front_desk.doctype.online_student_registration.online_student_registration.register_student",
//				frm: cur_frm
//			});
//		   }, __("Make"));
//		frm.add_custom_button(__("Appointment"), function() {
//			frappe.model.open_mapped_doc({
//				method: "front_desk.front_desk.doctype.online_student_registration.online_student_registration.make_appointment",
//				frm: cur_frm
//			});
//		   }, __("Make"));
//	},

	onload: function(frm) {
		frm.set_query('item_observation', function() {
			return {
				'filters': {
					'item_group': 'Observations'
				}
			};
		});
	},

	validate: function(frm) {
		var relation = frm.doc.guardian_relation
		var f_name = frm.doc.guardian_full_name
		var nationality = frm.doc.guardian_nationality
		var m_no = frm.doc.guardian_mobile_no
		switch (relation) {
			case "Father":
				frm.set_value("father_name", f_name);
				frm.set_value("father_nationality", nationality);
				frm.set_value("father_mob", m_no);
			break;
			case "Mother":
				frm.set_value("mother_name", f_name);
				frm.set_value("mother_nationality", nationality);
				frm.set_value("mother_mob", m_no);
			break;
		}
	},

	client_eid_no: function(frm) {
		var s1= frm.doc.client_eid_no
		if(s1.replace(/[0-9]/g, "")) {
			frm.set_value("client_eid_no", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	client_pod_no: function(frm) {
		var s2= frm.doc.client_pod_no
		if(s2.replace(/[0-9]/g, "")) {
			frm.set_value("client_pod_no", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	guardian_mobile_no: function(frm) {
		var s3= frm.doc.guardian_mobile_no
		if(s3.replace(/[0-9]/g, "")) {
			frm.set_value("guardian_mobile_no", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	guardian_id: function(frm) {
		var s4= frm.doc.guardian_id
		if(s4.replace(/[0-9]/g, "")) {
			frm.set_value("guardian_id", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	emergency_contact_no_1: function(frm) {
		var s5= frm.doc.emergency_contact_no_1
		if(s5.replace(/[0-9]/g, "")) {
			frm.set_value("emergency_contact_no_1", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	emergency_contact_no_2: function(frm) {
		var s6= frm.doc.emergency_contact_no_2
		if(s6.replace(/[0-9]/g, "")) {
			frm.set_value("emergency_contact_no_2", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	guardian_relation: function(frm) {
		var relation= frm.doc.guardian_relation
		if(relation=="Father") {
			frm.set_df_property("mother_name", "reqd", 1);
			frm.set_df_property("mother_nationality", "reqd", 1);
		}
		if(relation=="Mother") {
			frm.set_df_property("father_name", "reqd", 1);
			frm.set_df_property("father_nationality", "reqd", 1);
		}
		if(relation=="Others") {
			frm.set_df_property("father_name", "reqd", 1);
			frm.set_df_property("father_nationality", "reqd", 1);
			frm.set_df_property("mother_name", "reqd", 1);
			frm.set_df_property("mother_nationality", "reqd", 1);
		}
	},

	father_mob: function(frm) {
		var s7= frm.doc.father_mob
		if(s7.replace(/[0-9]/g, "")) {
			frm.set_value("father_mob", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	mother_mob: function(frm) {
		var s8= frm.doc.mother_mob
		if(s8.replace(/[0-9]/g, "")) {
			frm.set_value("mother_mob", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	persons_pickup1_mobile: function(frm) {
		var s8= frm.doc.mother_mob
		if(s8.replace(/[0-9]/g, "")) {
			frm.set_value("mother_mob", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	persons_pickup2_mobile: function(frm) {
		var s8= frm.doc.mother_mob
		if(s8.replace(/[0-9]/g, "")) {
			frm.set_value("mother_mob", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	persons_pickup3_mobile: function(frm) {
		var s8= frm.doc.mother_mob
		if(s8.replace(/[0-9]/g, "")) {
			frm.set_value("mother_mob", "");
			frappe.throw(__("Please use only numbers"));
		}
	},

	get_client_details: function(frm) {
		if (frm.doc.client && frm.doc.chk_date_of_birth) {
			frappe.call({
				method: "front_desk.front_desk.doctype.online_student_registration.online_student_registration.verify_student_details",
				args: {
					client_name: frm.doc.client,
					date_of_birth: frm.doc.chk_date_of_birth
				},
				callback: function(r) {
					frm.set_value("student_first_name", r.message.first_name);
					if (r.message.middle_name) {
						frm.set_value("student_middle_name", r.message.middle_name);
					}
					frm.set_value("student_last_name", r.message.last_name);
					frm.set_value("student_full_name", r.message.title);
					frm.set_value("date_of_birth", r.message.date_of_birth);
					frm.set_value("gender", r.message.gender);
					frm.set_value("religion", r.message.religion);
					frm.set_value("sibling_number", r.message.sibling_number);
					frm.set_value("language", r.message.language);
					frm.set_value("child_live_with", r.message.child_live_with);
					frm.set_value("parent_status", r.message.parent_status);
					frm.set_value("nationality", r.message.student_nationality);
					frm.set_value("place_of_birth", r.message.place_of_birth);
					frm.set_value("student_passport_no", r.message.student_passport_no);
					frm.set_value("expiry_date", r.message.expiry_date);
					frm.set_value("student_eid_no", r.message.student_eid_no);
					frm.set_value("eid_expiry_date", r.message.eid_expiry_date);

				}
			});
		} else {
			frappe.msgprint(__("Please enter Client ID and Date of Birth"));
		}
	}

});
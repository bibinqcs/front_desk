# Copyright (c) 2023, Quark Cyber Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WebsiteTrainingRegistration(Document):

    @frappe.whitelist()
    def create_customer(self):
        customer_name = self.first_name + self.last_name

        customer = frappe.new_doc("Customer")
        customer.update(
            {
                "customer_name": customer_name,
                "customer_type": "Individual",
                "territory": "United Arab Emirates",
                "customer_group": "ABAT Training",
                "from_website_training_registration_qcs": self.name,
            }
        )
        customer.insert(ignore_permissions=True)

        contact = frappe.new_doc("Contact")
        contact.update(
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
            }
        )

        if self.email:
            contact.append("email_ids", {"email_id": self.email, "is_primary": 1})

        if self.phone_number:
            contact.append("phone_nos", {"phone": self.phone_number, "is_primary_phone": 1, "is_primary_mobile_no": 1})

        contact.append("links", {"link_doctype": "Customer", "link_name": customer.name, "link_title": customer_name})

        contact.insert(ignore_permissions=True)

        customer.update(
            {
                "customer_primary_contact": contact.name
            }
        )
        customer.save(ignore_permissions=True)

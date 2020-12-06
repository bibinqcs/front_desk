<p>
{{ doc.employee_name }} has an attedance record with missing punch data.<br>
<br>
{{ frappe.utils.get_url_to_form(doc.doctype, doc.name) }}<br>
</p>
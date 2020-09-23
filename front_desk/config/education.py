from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Admission"),
            "icon": "fa fa-star",
            "items": [
                {
                    "type": "doctype",
                    "name": "Online Student Registration",
                    "description": _("Online Student Registration."),
                },
            ]
        },
    ]

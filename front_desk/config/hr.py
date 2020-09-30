from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Attendance"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Biometric Access Log",
                    "description": _("Biometric Access Log"),
                },
            ]
        },
                {
            "label": _("Settings"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Suprema Biometric Device Integration",
                    "description": _("Suprema Biometric Device Integration"),
                },
            ]
        },
    ]

CRND Web Actions
================

.. |badge2| image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

.. |badge3| image:: https://img.shields.io/badge/powered%20by-yodoo.systems-00a09d.png
    :target: https://yodoo.systems

.. |badge5| image:: https://img.shields.io/badge/maintainer-CR&D-purple.png
    :target: https://crnd.pro/

.. |badge4| image:: https://img.shields.io/badge/docs-Website_Service_Desk-yellowgreen.png
    :target: https://crnd.pro/doc-bureaucrat-itsm/11.0/en/Website_Service_Desk_eng/


|badge2| |badge4| |badge5|

CRND Web Actions

::

    def action_reload(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'crnd_act_nothing'/'crnd_act_view_reload',
        }

If you use the 'crnd_act_view_reload' action, there is no edit mode check by default. If you do not want to reload a view that is not saved, then add to the button:

::

    context="{'force_reload': False}"

Launch your own ITSM system in 60 seconds:
''''''''''''''''''''''''''''''''''''''''''

Create your own `Bureaucrat ITSM <https://yodoo.systems/saas/template/bureaucrat-itsm-demo-data-95>`__ database

|badge3|


Bug Tracker
===========

Bugs are tracked on `https://crnd.pro/requests <https://crnd.pro/requests>`_.
In case of trouble, please report there.


Maintainer
''''''''''
.. image:: https://crnd.pro/web/image/3699/300x140/crnd.png

Our web site: https://crnd.pro/

This module is maintained by the Center of Research & Development company.

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions `contact us <mailto:info@crnd.pro>`__.

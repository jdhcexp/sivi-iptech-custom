from odoo.addons.crnd_wsd.tests.phantom_common import (
    TestPhantomTour
)


class TestCrndWsdProject(TestPhantomTour):

    def setUp(self):
        super(TestCrndWsdProject, self).setUp()
        self.user_demo = self.env.ref(
            'crnd_wsd.user_demo_service_desk_website')
        self.project = self.env.ref(
            'generic_request_project.request_with_task_project_1')

    def test_request_with_task(self):
        # Assign user_demo to grant access to project
        # In Odoo 16 Project customer no more default project follower
        self.project.message_subscribe(
            partner_ids=self.user_demo.partner_id.ids)
        self.assertIn(self.user_demo.partner_id,
                      self.project.message_follower_ids.mapped('partner_id'))
        self._test_phantom_tour(
            '/', 'crnd_wsd_project_request_with_task',
            login=self.user_demo.login)

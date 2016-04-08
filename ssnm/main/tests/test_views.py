'''
This file is to test all the views of the application.
'''
from ssnm.main.models import Ecomap
from ssnm.main.views import get_map_details, show_maps, delete_map
from ssnm.main.views import get_map, go_home
from ssnm.main.views import logout, display
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


class SimpleViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_smoketest(self):
        """ just run the smoketests. we don't care if they pass/fail """
        self.client.get("/smoketest/")


class TestView(TestCase):
    def setUp(self):
        '''Set up method for testing views.'''
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'somestudent', 'email@email.com', 'somestudent')
        self.user.set_password("test")
        self.user.save()
        # IF BELOW VIEWS ARE COMMENTED OUT ALMOST EVERYTHING PASSES
        self.ecomap = Ecomap(
            pk='6', name="Test Map 1",
            ecomap_xml=(
                "<data><response>OK</response><isreadonly>false"
                "</isreadonly><name>somestudent</name><flashData>"
                "<circles><circle><radius>499</radius></circle>"
                "<circle><radius>350</radius></circle><circle>"
                "<radius>200</radius></circle></circles>"
                "<supportLevels><supportLevel><text>VeryHelpful</text>"
                "</supportLevel><supportLevel><text>SomewhatHelpful"
                "</text></supportLevel><supportLevel><text>"
                "NotSoHelpful</text></supportLevel></supportLevels>"
                "<supportTypes><supportType><text>Social</text>"
                "</supportType><supportType><text>Advice</text>"
                "</supportType><supportType><text>Empathy</text>"
                "</supportType><supportType><text>Practical</text>"
                "</supportType></supportTypes><persons><person><name>"
                "green</name><supportLevel>2</supportLevel>"
                "<supportTypes><support>Advice</support><support>"
                "Social</support></supportTypes><x>293</x><y>70</y>"
                "</person><person><name>yellow</name><supportLevel>1"
                "</supportLevel><supportTypes><support>Social</support>"
                "<support>Empathy</support></supportTypes><x>448</x>"
                "<y>208</y></person><person><name>red</name>"
                "<supportLevel>0</supportLevel><supportTypes>"
                "<support>Social</support><support>Practical"
                "</support></supportTypes><x>550</x><y>81.95</y>"
                "</person></persons></flashData></data>"))
        self.ecomap.owner = self.user
        self.ecomap.save()
        # unauthenticated user
        self.bad_user = User.objects.create_user(
            'not_ecouser', 'email@email.com', 'not_ecouser')
        self.bad_user.save()

    # FIRST CHECK THAT ALL URLS ARE ACCESSIBLE
    # following three pass whether using client or the above user info
    def test_about(self):
        '''Test that requesting about page returns a response.'''
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('about.html')

    def test_help(self):
        '''Test that requesting help page returns a response.'''
        response = self.client.get('/help/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('help.html')

    def test_contact(self):
        '''Test that requesting contact page returns a response.'''
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contact.html')

    def test_thanks(self):
        '''Test that requesting thanks page returns a response.'''
        response = self.client.get('/thanks/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('thanks.html')

    # Contact Form
    def test_contact_form(self):
        response = self.client.post(
            '/contact/',
            {"subject": "subject here", "message": "message here",
             "sender": "sender", "recipients": "test_email@email.com"})
        response.user = self.user
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('thanks.html')

    def test_contact_form_not_valid(self):
        response = self.client.post(
            '/contact/',
            {"subject": "", "message": "",
             "sender": "", "recipients": "someone"})
        response.user = self.user
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contact.html')

    def test_details_empty_form(self):
        '''Test that user who creates account get appropriate response.'''
        self.client.login(
            username=self.user.username,
            password="test")
        response = self.client.get('/details/6/')
        response.user = self.user
        self.assertEqual(response.status_code, 200)

    def test_details_with_form_get(self):
        '''Test that user who creates account get appropriate response.'''
        request = self.factory.get('/details/')
        request.user = self.user
        response = get_map_details(request, map_id="")
        self.assertEqual(response.status_code, 200)

    def test_details_with_form_post(self):
        '''Test that user who creates account get appropriate response.'''
        new_xml = """<data>
            <response>OK</response>
            <isreadonly>false</isreadonly>
            <name>New Map Name</name>
            <flashData>
            <circles>
            <circle><radius>499</radius></circle>
            <circle><radius>350</radius></circle>
            <circle><radius>200</radius></circle>
            </circles>
            <supportLevels>
            <supportLevel><text>Very Helpful</text>
            </supportLevel>
            <supportLevel><text>Somewhat Helpful</text>
            </supportLevel>
            <supportLevel><text>Not So Helpful</text>
            </supportLevel>
            </supportLevels>
            <supportTypes>
            <supportType><text>Social</text></supportType>
            <supportType><text>Advice</text></supportType>
            <supportType><text>Empathy</text></supportType>
            <supportType><text>Practical</text></supportType>
            </supportTypes>
            <persons></persons>
            </flashData>
            </data>"""
        request = self.factory.post(
            '/details/', {"name": "some_map",
                          "ecomap.description": "this is the maps description",
                          "ecomap.ecomap_xml": new_xml})
        request.user = self.user
        response = get_map_details(request, map_id="")
        self.assertEqual(response.status_code, 302)

    def test_show_maps(self):
        '''Test that logged in user recieves response of home page.'''
        request = self.factory.post('/show_maps/')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)

    def test_go_home(self):
        '''Test back to maps button in flash returns to map list.'''
        request = self.factory.post(
            'ecomap/6/display/back_to_list_button_clicked')
        request.user = self.user
        response = go_home(request, 6)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("map_page.html")

    # #  TEST RETRIEVAL OF SAVE MAP
    def test_saved_ecomap(self):
        '''Test that requesting saved_ecomap page returns a response.'''
        request = self.factory.post('/ecomap/6/')
        request.user = self.user
        response = get_map(request, 6)
        self.assertEqual(response.status_code, 200)

    def test_delete_map(self):
        request = self.factory.post('/delete_map/6/')
        request.user = self.user
        delete_map(request, 6)
        with self.assertRaises(Ecomap.DoesNotExist):
            Ecomap.objects.get(pk=6)

    def test_logout(self):
        request = self.factory.post('/logout/')
        request.user = self.user
        response = logout(request)
        self.assertEqual(response.status_code, 302)

    # TEST FLASH IS RETURNING RESPONSE
    def test_flash_ecomap(self):
        '''Test that requesting ecomap_page's flash conduit
        returns a response.'''
        request = self.factory.post('/ecomap/display/flashConduit')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)

    def test_saved_flash_ecomap(self):
        '''Test that requesting saved_ecomap_page's flash conduit
        returns a response.'''
        request = self.factory.post('/ecomap/6/display/flashConduit')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)

    def test_saved_flash(self):
        request = self.factory.post('/ecomap/6/display/flashConduit')
        request.user = self.user
        response = display(request, 6)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('game_test.html')

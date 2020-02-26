from django.test import TestCase
from django.urls import reverse

from .models import Agent, Recording


# Create your tests here.
class IVRViewsTest(TestCase):
    def test_index(self):
        response = self.client.get(reverse('ivr:index'))
        self.assertEqual(response.status_code, 200)

    def test_agents(self):
        response = self.client.get(reverse('ivr:agents'))
        self.assertEqual(response.status_code, 200)

    def test_welcome(self):
        response = self.client.post(reverse('ivr:welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Gather action="/ivr/menu/" numDigits="1">'
            b'<Play loop="3">https://can-tasty-8188.twil.io/assets/et-phone.mp3</Play>'
            b'</Gather></Response>',
        )

    def test_menu_instructions_option(self):
        response = self.client.post(reverse('ivr:menu'), {'Digits': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Say language="en-GB" voice="alice">To get to your extraction point, get on your bike and go down the street. Then Left down an alley. Avoid the police cars. Turn left into an unfinished housing development. Fly over the roadblock. Go passed the moon. Soon after you will see your mother ship.</Say>'
            b'<Say>Thank you for calling the ET Phone Home Service - the adventurous alien\'s first choice in intergalactic travel</Say>'
            b'<Hangup /></Response>',
        )

    def test_menu_planets_option(self):
        response = self.client.post(reverse('ivr:menu'), {'Digits': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Gather action="/ivr/agent/connect" numDigits="1">'
            b'<Say language="en-GB" loop="3" voice="alice">To call the planet Broh doe As O G, press 2. To call the planet DuhGo bah, press 3. To call an oober asteroid to your location, press 4. To go back to the main menu, press the star key </Say>'
            b'</Gather></Response>',
        )

    def test_menu_invalid_option(self):
        response = self.client.post(reverse('ivr:menu'), {'Digits': '6'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?><Response><Redirect>/ivr/welcome/</Redirect></Response>',
        )

    def test_agent_connect_valid(self):
        Agent.objects.create(name='Brodo', phone_number='1234567890')
        response = self.client.post(reverse('ivr:agent_connect'), {'Digits': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Say language="en-GB" voice="alice">You\'ll be connected shortly to your planet.</Say>'
            b'<Dial action="/ivr/agent/call?agentId=1" callerId="1234567890">'
            b'<Number url="/ivr/agent/screencall">1234567890</Number>'
            b'</Dial></Response>',
        )

    def test_agent_connect_invalid(self):
        response = self.client.post(reverse('ivr:agent_connect'), {'Digits': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?><Response><Redirect>/ivr/welcome/</Redirect></Response>',
        )

    def test_agent_call_completed(self):
        response = self.client.post(
            reverse('ivr:agents_call'), {'CallStatus': 'completed'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    def test_agent_call_not_completed(self):
        response = self.client.post(
            f"{reverse('ivr:agents_call')}?agentId=1", {'CallStatus': 'ongoing'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Say language="en-GB" voice="alice">It appears that no agent is available. Please leave a message after the beep</Say>'
            b'<Record action="/ivr/agent/hangup" maxLength="20" transcribeCallback="/ivr/agent/recordings?agentId=1" />'
            b'</Response>',
        )

    def test_hangup(self):
        response = self.client.post(reverse('ivr:hangup'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Say language="en-GB" voice="alice">Thanks for your message. Goodbye</Say>'
            b'<Hangup /></Response>',
        )

    def test_screencall(self):
        response = self.client.post(
            reverse('ivr:agents_screencall'), {'From': '1234567890'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Gather action="/ivr/agent/connect_message"><Say>1 2 3 4 5 6 7 8 9 0</Say><Say>Press any key to accept</Say></Gather>'
            b'<Say>Sorry. Did not get your response</Say><Hangup /></Response>',
        )

    def test_connect_message(self):
        response = self.client.post(reverse('ivr:agents_connect_message'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<Response><Say>Connecting you to the extraterrestrial in distress</Say></Response>',
        )

    def test_create_recordings(self):
        Agent.objects.create(name='Brodo', phone_number='222222222')
        response = self.client.post(
            f"{reverse('ivr:recordings')}?agentId=1", {
                'From': '1234567890',
                'TranscriptionText': 'Sample',
                'RecordingUrl': '/test/url'
                }
        )
        self.assertEqual(response.status_code, 201)
        recordings_count = Recording.objects.count()
        self.assertEqual(recordings_count, 1)

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import Say, VoiceResponse

from .models import Agent, Recording


def index(request):
    context = {'title': 'Sample IVR Recordings'}
    return render(request, 'ivr/index.html', context)


def agents(request):
    agents = Agent.objects.order_by('name')
    context = {'agents': agents}
    return render(request, 'ivr/agents.html', context)


@csrf_exempt
def welcome(request):
    twiml_response = VoiceResponse()
    gather = twiml_response.gather(action=reverse('ivr:menu'), num_digits=1)
    gather.play('https://can-tasty-8188.twil.io/assets/et-phone.mp3', loop=3)
    return HttpResponse(twiml_response, content_type='application/xml')


# MAIN MENU


@csrf_exempt
def menu(request):
    selected_option = request.POST['Digits']
    options = {
        '1': return_instructions,
        '2': planets,
    }
    action = options.get(selected_option) or redirect_welcome
    return HttpResponse(str(action()))


def return_instructions():
    twiml_response = VoiceResponse()
    twiml_response.say(
        'To get to your extraction point, get on your bike and go down '
        'the street. Then Left down an alley. Avoid the police cars.'
        ' Turn left into an unfinished housing development. Fly over '
        'the roadblock. Go passed the moon. Soon after you will see '
        'your mother ship.',
        voice='alice',
        language='en-GB',
    )
    twiml_response.say(
        'Thank you for calling the ET Phone Home Service - the '
        'adventurous alien\'s first choice in intergalactic travel'
    )
    twiml_response.hangup()
    return twiml_response


def planets():
    twiml_response = VoiceResponse()
    gather = twiml_response.gather(action=reverse('ivr:agent_connect'), num_digits=1)
    gather.say(
        'To call the planet Broh doe As O G, press 2. To call the '
        'planet DuhGo bah, press 3. To call an oober asteroid to your '
        'location, press 4. To go back to the main menu, press '
        'the star key ',
        voice='alice',
        language='en-GB',
        loop=3,
    )
    return twiml_response


def redirect_welcome():
    twiml = VoiceResponse()
    twiml.redirect('/ivr/welcome/')
    return twiml


# AGENTS


@csrf_exempt
def agent_connect(request):
    selected_option = request.POST.get('Digits')
    agents = {
        '2': 'Brodo',
        '3': 'Dagobah',
        '4': 'Oober',
    }
    selected_agent = agents.get(selected_option)
    if selected_agent is None:
        # Bad user input
        return HttpResponse(str(redirect_welcome()))
    agent = Agent.objects.get(name=selected_agent)
    if agent is None:
        # Agent doesn't exist on DB
        return HttpResponse(str(redirect_welcome()))

    twiml = VoiceResponse()
    try:
        twiml.say(
            'You\'ll be connected shortly to your planet.',
            voice='alice',
            language='en-GB',
        )
        dial = twiml.dial(
            action=f"{reverse('ivr:agents_call')}?agentId={agent.id}",
            callerId=agent.phone_number,
        )
        dial.number(agent.phone_number, url=reverse('ivr:agents_screencall'))
        return HttpResponse(str(twiml))
    except:
        return HttpResponseServerError('An error has ocurred')


@csrf_exempt
def agent_call(request):
    if request.POST['CallStatus'] == 'completed':
        return HttpResponse('')
    twiml = VoiceResponse()
    twiml.say(
        'It appears that no agent is available. '
        'Please leave a message after the beep',
        voice='alice',
        language='en-GB',
    )
    twiml.record(
        max_length=20,
        action=reverse('ivr:hangup'),
        transcribe_callback=f"{reverse('ivr:recordings')}?agentId={request.GET.get('agentId')}",
    )
    return HttpResponse(str(twiml))


@csrf_exempt
def hangup(request):
    twiml = VoiceResponse()
    twiml.say(
        'Thanks for your message. Goodbye', voice='alice', language='en-GB',
    )
    twiml.hangup()
    return HttpResponse(str(twiml))


@csrf_exempt
def screencall(request):
    twiml = VoiceResponse()
    gather = twiml.gather(action=reverse('ivr:agents_connect_message'))
    phone_number = request.POST['From']
    spelled_phone_number = ' '.join(char for char in phone_number)
    gather.say(spelled_phone_number)
    gather.say('Press any key to accept')
    twiml.say('Sorry. Did not get your response')
    twiml.hangup()
    return HttpResponse(str(twiml))


@csrf_exempt
def connect_message(request):
    twiml = VoiceResponse()
    twiml.say('Connecting you to the extraterrestrial in distress')
    return HttpResponse(str(twiml))


# RECORDINGS

@csrf_exempt
def recordings(request):
    agentId = request.GET.get('agentId')
    agent = Agent.objects.get(pk=agentId)
    try:
        recording = Recording.objects.create(
            caller_number=request.POST['From'],
            transcription=request.POST['TranscriptionText'],
            url=request.POST['RecordingUrl'],
        )
        agent.recordings.add(recording)
        return HttpResponse('Recording created', status=201)
    except:
        return HttpResponseServerError('Could not create a recording')

<a href="https://www.twilio.com">
  <img src="https://static0.twilio.com/marketing/bundles/marketing/img/logos/wordmark-red.svg" alt="Twilio" width="250" />
</a>

# IVR Call Recording and Agent Conference.

IVRs (interactive voice response) are automated phone systems that can facilitate communication between callers and businesses. In this tutorial you will learn how to screen and send callers to voicemail if an agent is busy.

[Read the full tutorial here](https://www.twilio.com/docs/tutorials/walkthrough/ivr-screening/python/django)!

[![Build and test](https://github.com/TwilioDevEd/ivr-recording-django/actions/workflows/build_test.yml/badge.svg)](https://github.com/TwilioDevEd/ivr-recording-django/actions/workflows/build_test.yml)

## Local Development

1. Clone this repository and `cd` into its directory:

   ```bash
   git clone git@github.com:TwilioDevEd/ivr-recording-django.git
   cd ivr-recording-django
   ```

1. The file `ivr/fixtures/agents.json` contains the agents phone numbers. Replace any of these phone numbers with yours.

    When the application asks you to select an agent, choose the one you just modified and it will then call your phone.

1. Create a local virtual environment and activate it:

   ```bash
   python -m venv venv && source venv/bin/activate
   ```

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

1. Set environment variables:

   ```bash
   cp .env.example .env
   ```
   Then add a value to `SECRET_KEY`.

1. Set up database and run migrations:

   ```bash
   python manage.py migrate
   ```

1. Load initial agents' data:

   ```bash
   python manage.py loaddata ivr/fixtures/agents.json
   ```

1. Make sure the tests succeed:

    ```bash
    python manage.py test
    ```

1. Run the application:

    ```bash
    python manage.py runserver
    ```

1. Check it out at [http://localhost:8000/ivr](http://localhost:8000/ivr).
   You can go to the [agents page](http://localhost:8000/ivr/agents) to see and listen the saved recordings.

1. Expose the application to the wider Internet using [ngrok](https://ngrok.com/)
   To let our Twilio Phone number use the callback endpoint we exposed, our development server will need to be publicly accessible. [We recommend using ngrok to solve this problem](https://www.twilio.com/blog/2015/09/6-awesome-reasons-to-use-ngrok-when-testing-webhooks.html).

   ```bash
   ngrok http 8000
   ```

1. Provision a number under the [Manage Numbers page](https://www.twilio.com/user/account/phone-numbers/incoming) on your account. Set the voice URL for the number to `http://<your-ngrok-subdomain>.ngrok.io/ivr/welcome`.

That's it!

## Meta

* No warranty expressed or implied. Software is as is. Diggity.
* [MIT License](http://www.opensource.org/licenses/mit-license.html)
* Lovingly crafted by Twilio Developer Education.

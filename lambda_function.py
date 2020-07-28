import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

# This code is based on a tutorial found at:
# https://medium.com/datadriveninvestor/building-your-own-alexa-skill-from-scratch-2019-edition-957d776e22d5

is_fed = False
user_id = ''
# make the connection to dynamodb
dynamodb = boto3.resource('dynamodb')


# main handler method


def lambda_handler(event, context):
    if event['session']['new']:
        on_start()
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event)
    elif event['request']['type'] == "IntentRequest":
        return intent_scheme(event)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end()

# BASE METHODS


def on_start():
    print("Session Started.")


def on_launch(event):
    global user_id
    onlunch_MSG = "Hi, and welcome to have the pets been fed"
    user = event['context']['System']['user']
    print(event['context']['System']['user'])
    user_id = user['userId']
    reprompt_MSG = "Have the pets been fed?"
    card_TEXT = "Tell us whether the pets have been fed."
    card_TITLE = "Fed a pet."
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def on_end():
    print("Session Ended.")


def intent_scheme(event):
    intent_name = event['request']['intent']['name']
    if intent_name == "petsFed":
        return feed_the_pet(event)
    elif intent_name == "set_pet_fed":
        return set_pet_fed(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)


# CUSTOM METHODS


def feed_the_pet(event):
    # pet_name = event['request']['intent']['slots']['pet']['value']
    if (is_fed):
        fed_MSG = "The pet has been fed"
    else:
        fed_MSG = "The pet has not been fed"

    reprompt_MSG = "I'm sorry, I didn't understand you?"
    card_TEXT = "Has the pet been fed."
    card_TITLE = "Has the pet been fed."
    print(output_json_builder_with_reprompt_and_card(
        fed_MSG, card_TEXT, card_TITLE, reprompt_MSG, False))
    return output_json_builder_with_reprompt_and_card(fed_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)

# TODO - A method to save the pet name


def set_pet_fed(event):
    global is_fed
    global user_id
    is_fed = True
    fed_MSG = "Thank you, we will remember that the pet has been fed"
    reprompt_MSG = "I'm sorry, has the pet been fed?"
    card_TEXT = "Feed the pet."
    card_TITLE = "Feed the pet."
    table = dynamodb.Table('User')
    print('this is the user id ' + user_id)
    response = table.query(KeyConditionExpression=Key('user_id').eq(user_id))
    print(response)
    if(response['Items'] == []):
        response = table.put_item(
            Item={
                'user_id': user_id
            }
        )
    print(response)
    print(output_json_builder_with_reprompt_and_card(
        fed_MSG, card_TEXT, card_TITLE, reprompt_MSG, False))
    return output_json_builder_with_reprompt_and_card(fed_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def stop_the_skill(event):
    stop_MSG = "Thank you. Bye!"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True)


def assistance(event):
    assistance_MSG = "You can ask if the cat has been fed. You can tell us if the cat has been fed."
    reprompt_MSG = "Do you want to know if the cat has been fed, or tell Alexa that it has?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def fallback_call(event):
    fallback_MSG = "I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to know if the cat has been fed, or tell Alexa that it has?"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)

# UTILITY METHODS


def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict


def reprompt_builder(repr_text):
    reprompt_dict = {}
    reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    return reprompt_dict


def card_builder(c_text, c_title):
    card_dict = {}
    card_dict['type'] = "Simple"
    card_dict['title'] = c_title
    card_dict['content'] = c_text
    return card_dict


def response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    speech_dict = {}
    speech_dict['outputSpeech'] = plain_text_builder(outputSpeach_text)
    speech_dict['card'] = card_builder(card_text, card_title)
    speech_dict['reprompt'] = reprompt_builder(reprompt_text)
    speech_dict['shouldEndSession'] = value
    return speech_dict


def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    response_dict = {}
    response_dict['version'] = '1.0'
    response_dict['response'] = response_field_builder_with_reprompt_and_card(
        outputSpeach_text, card_text, card_title, reprompt_text, value)
    return response_dict

import json


def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def on_start():
    print("Session Started.")


def on_launch(event):
    onlunch_MSG = "Hi, and welcome to have the pets been fed"
    reprompt_MSG = "Have the pets been fed?"
    card_TEXT = "Tell us whether the pets have been fed."
    card_TITLE = "Fed a pet."
    return output_json_builder_with_reprompt_and_card(onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


def on_end():
    print("Session Ended.")


def intent_scheme(event):
    # change this intent name
    intent_name = event['request']['intent']['name']if intent_name == "feedThePet":
        return feed_the_pet(event)
    elif intent_name in ["AMAZON.NoIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)

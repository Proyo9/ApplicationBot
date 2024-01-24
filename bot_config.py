version = "1.0.0" # DO NOT CHANGE

config = {
    "apply_command": True, # If you want the /apply command to be enabled
    "application_catagory": 0, # The catagory ID where the applications will be sent
    "application_team": 0, # Role ID of the team that can manage the applications
    "messages": {
        "application_sent": "Application sent!", # The message that will be sent to the user when the application is sent
        "application_new": "<@&role_id> New Application", # The message that will be sent in the user's application channel (Can be used to ping a role)
        "application_accepted": "Your application has been accepted, {user}.", # Acceptance message
        "application_denied": "Your application has been denied, {user}.", # Denial message
    },
    "auto_update": True, # You should keep this on unless you are familiar with py-cord and want to self-maintain the bot
}

applications = {
    "Staff": {
        "description": "Apply for staff!",
        "enabled": True,
        "max_applications": 1, # Amount of applications a user can have open at once (0 for unlimited)
        "questions": {
            "What is your name?": {
            "length": "short",
            "placeholder": "Type your answer here",
            "required": True,
            },
            "How old are you?": {
                "length": "short",
                "placeholder": "Type your answer here",
                "required": True,
            },
            "Why should we accept you among others?": {
                "length": "long",
                "placeholder": "Type your answer here",
                "required": True,
            }
        }
    },
}

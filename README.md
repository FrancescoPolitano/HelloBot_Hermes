# HelloBot_Hermes
Hermes group's project for the "HelloBot" hackaton powered by HKN. [WINNER]

[RestfulService]
The restfulService aggregates and exposes all the information about the resources.
Cause of the limited time and resources of an hackaton and cause of the varius assumptions
maked in design fase some resources are hardcoded or obtained in unconventional and sub-optimal ways.

[Sensor]
A movement sensor realized using a RaspBerry PI 3. It realizes simple POST requests for real-time monitoration.

[ErmesTObot]
A Bot for Telegram, written in Python and based on a flow of events realized as a states machine.
The bot tracks users state storing it and any other information on the noSQL database provided by
the Google Cloude Platform App Engine in which the bot is deployed.

The bot act as a friendly UI for the user that can easily accede the data provided by the REST API.

This git contains also a basic flowchart as a result of the design fase of the UX and the slides presented during the hackaton.


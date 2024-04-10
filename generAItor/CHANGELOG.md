# Changelog

1.0.0 - (2024-03-11)
--------------------
* Functional version of the tool as a service with two main APIs:
  * `/analyze`: Used to check if the zip file passed as parameter is well-formed.
  * `/generate`: Used to generate code based on the zip information passed as parameter.

0.0.9 - (2024-02-27)
--------------------
* Making the tool usable as a service (through APIs)

0.0.8 - (2024-02-09)
--------------------
* Making the tool usable with dynamic config checking (output target files can be used as inputs target ones)

0.0.7 - (2023-11-17)
--------------------
* Adding 'generate' extra field under the config file with its corresponding
validations

0.0.6 - (2023-09-08)
--------------------
* Removing code-stats (using `pygount`) when running on a frozen Windows 
* system (like the one created using `pyinstaller`).


0.0.5 - (2023-08-30)
--------------------
* Fixing env vars to check if AZURE_API_BASE_ENV_NAME is a valid URL.
* Changes on `check-credentials` to use the OpenAI env vars to retry.


0.0.4 - (2023-08-30)
--------------------
* Fix to read env variables with recurse=False only for 
* Windows if it's running on a bundled (`pyinstaller`) system.


0.0.3 - (2023-08-24)
--------------------
* Adding env vars to calculate charges.
* Changes to show the complete path of the targets.


0.0.2 - (2023-08-24)
--------------------
* Minor changes to support {root} on config.


0.0.1 - (2023-08-22)
--------------------
* Working version.


1.0.0 - (2023-08-14)
--------------------
* Initial version.
* Project begins.
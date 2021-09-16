# ACG Project: DIY Mars Probe
## AWS Greengrass IoT v2 with a Raspberry Pi Zero W

This repo is the companion to the [ACG Project: DIY Mars Probe](https://acloud.guru/series/acg-projects/view/405) and a two-part blog published on [Code Project](https://www.codeproject.com/).

The Greengrass v2 recipies and basic Python code is provided as a starting point.  The idea is that you can fork this repo and start your own experimentation with [AWS Greengrass IoT v2](https://docs.aws.amazon.com/greengrass/v2/developerguide/greengrass-v2-whats-new.html).  If you see blatant errors, feel free to create a pull request.

## Contents
| File/Location                        | Description                                                                                                                                                                               |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [HardwareSetup.md](HardwareSetup.md) | Contains some more specifics about the hardware used and the process for installing and setting up the hardware libraries and drivers.  Also includes some issues I encountered and tips. |
| ```src/artifacts```                  | The Python code used in the ACG Project and blog articles                                                                                                                                 |
| ```src/iam```                        | The IAM roles in JSON format used in the ACG Project                                                                                                                                      |
| ```src/recipes```                    | The recipes used for both custom components in the ACG Project                                                                                                                            |

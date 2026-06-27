# Aldi Talk Integration for Home Assistant

This custom component for Home Assistant allows users to access their Aldi Talk account data directly within Home Assistant, providing a convenient way to monitor account details such as account balance, data volume, and validity periods.

![Version](https://img.shields.io/github/v/release/JonasJoKuJonas/homeassistant-AldiTalk)
[![Downloads](https://img.shields.io/github/downloads/JonasJoKuJonas/homeassistant-AldiTalk/total)](https://tooomm.github.io/github-release-stats/?username=JonasJoKuJonas&repository=homeassistant-AldiTalk)
![HACS Install Badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20installations&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.aldi_talk.total)
[![Latest Release](https://img.shields.io/github/release-date/JonasJoKuJonas/homeassistant-AldiTalk?style=flat&label=Latest%20Release)](https://github.com/JonasJoKuJonas/homeassistant-Aldi-Talk/releases)
[![Open Issues](https://img.shields.io/github/issues/JonasJoKuJonas/homeassistant-AldiTalk?style=flat&label=Open%20Issues)](https://github.com/JonasJoKuJonas/homeassistant-AldiTalk/issues)

## Disclaimer

This component uses web scraping, not an official Aldi Talk API. It may be subject to errors or changes in Aldi Talk's website structure that could affect functionality.
Use this component at your own risk, understanding potential risks including account issues or violations of Aldi Talk's terms. The developers are not affiliated with Aldi Talk and are not liable for any damages resulting from its use. Your use indicates acceptance of these risks.

## Instalation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JonasJoKuJonas&repository=homeassistant-AldiTalk&category=Integration)

1. Download
2. Reboot
3. Setup

## Setup Instructions

1. Ensure you have your [Aldi Talk login credentials](https://login.alditalk-kundenbetreuung.de/sso/UI/Login?service=login) ready.
2. Use these credentials to set up the Aldi Talk integration via Home Assistant's UI.

## Available Sensors

This component provides access to the following sensors within Home Assistant, allowing you to monitor various aspects of your Aldi Talk account:

| Sensor Name           | Description                      | Domain                                |
| --------------------- | -------------------------------- | ------------------------------------- |
| Account Balance       | The current account balance.     | `sensor.<name>_account_balance`       |
| Start Day             | The start date of the plan.      | `sensor.<name>_start_day`             |
| End Day               | The expiration date of the plan. | `sensor.<name>_end_day`               |
| Total Data Volume     | Total data volume available.     | `sensor.<name>_total_data_volume`     |
| Remaining Data Volume | Data volume remaining.           | `sensor.<name>_remaining_data_volume` |

The data will update every 30 minutes.

You can change the unit of measurement via the entity configuration to display it in GB

## Dashboard

For a beautiful and ready-to-use way to display your Aldi Talk data on your Home Assistant dashboard, check out the custom Lovelace card designed for this integration:

**[Aldi Talk Lovelace Card](https://github.com/jvilhuber/lovelace-aldi-talk-card)**

It provides a clean overview of your account status, including data usage, remaining volume, and validity periods, making it easy to monitor everything at a glance.



[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/Jonas_JoKu)

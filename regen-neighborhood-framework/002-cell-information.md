---
title: The Cell — Information Domain
number: 002
level: cell
domain: information
---

# The Cell — Information Domain

IoT stands for Internet of Things.
It means sensors connected to a network.
A sensor measures physical quantity.
It sends the reading over the network.

A microcontroller runs at 240MHz.
It costs $5.
It has WiFi.
It can run IoT software.

A temperature and humidity sensor costs $3.
It measures apparent temperature.
It measures relative humidity.

The microcontroller reads the sensor.
It stores the reading.
It sends the reading over WiFi.
This is the smallest possible sensing system.

MQTT stands for Message Queuing Telemetry Transport.
It is a sensor network protocol.
The microcontroller publishes to a topic.
A server subscribes to the topic.
The topic name tells you what the reading means.

One reading per hour is enough for most purposes.
That is 24 readings per day.

Store readings in a database.
A time-series database holds the readings with timestamps.
It answers what was the value at time X.

A hidden variable is something you cannot measure directly.
An example is true temperature.
A sensor measures apparent temperature.
The difference is sensor error.

Bayesian inference separates the hidden true value from sensor noise.
Prior belief is what you thought before the reading.
Posterior belief is what you think after.
The formula is simple.
Posterior is proportional to Prior times Likelihood.

Likelihood measures how likely the reading is given the current belief.

weather_state is one shared hidden variable.
All sensors contribute to it.
It represents the real state of the environment.

The model is this.
Sensor reading equals true value plus noise.
Noise has a distribution.
Bayesian inference finds the distribution of the true value.

This math applies to temperature.
It applies to humidity.
It applies to water level.
It applies to soil moisture.
It applies to battery voltage.
Learn it once.
Use it everywhere.

Store beliefs in a knowledge graph database.
Each belief has a mean.
Each belief has a variance.
Variance tells you how sure the system is.
Low variance means high confidence.
High variance means low confidence.

The goal is to reduce variance over time.
More readings mean more confidence.

The cell information layer feeds into the tissue information layer.
When two people share sensors they share the weather_state.
This is how collective sensing begins.
One reading at a time.

See [001], [011], [021].

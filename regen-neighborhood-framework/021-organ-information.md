---
title: The Organ — Information Domain
number: 021
level: organ
domain: information
---

# The Organ — Information Domain

An organ is one neighborhood.
Twelve to 200 people.

A neighborhood sensor mesh covers the area.
Each home has one node.
Each water tank has one node.
Each garden has one node.

Nodes form a mesh network.
They talk to each other.
They talk to a server.
The server runs a knowledge graph database.
It holds beliefs.
It holds relations between beliefs.

The server runs a time-series database.
It holds sensor readings.
Each reading has a timestamp.
It answers what was the value at time X.

One shared latent variable connects all sensors.
This variable represents real environment state.
Weather. Humidity. Soil moisture. Water level. Battery voltage.

Bayesian inference updates the variable.
New readings narrow the distribution.
More sensors narrow it faster.
The model captures correlations.

Rain raises the water tank.
Rain raises the soil moisture.
High temperature increases evaporation.
High humidity slows evaporation.
The system sees these connections.

A digital twin mirrors the physical neighborhood.
It updates as sensors update.
It runs predictions.
It shows what might go wrong.

All data stays in the commons.
No cloud service owns the data.
The organ owns it.

Hardware costs $50 for the server.
A small computer runs the software.
The system queues data if the server fails.
No readings are lost.
When the server recovers sensors send queued data.

Sensors cost $3 to $10 each.
A full neighborhood mesh costs $200 to $1,000.
Installation is DIY.
Maintenance is sensor replacement.

See [002], [020], [023], [040].

---
title: Drone Swarms — Physical Infrastructure for FCL
number: 052
level: organ
domain: physical
---

# Drone Swarms — Physical Infrastructure for FCL

Autonomous aerial vehicles (AAVs) carry LEDs.
They form shapes in the sky.
Each vehicle holds a position.
Together they form a formation.
A formation sends a message.
The message is the shape.
Formation Coding Language (FCL) defines how shapes encode meaning.
The swarm is the hardware layer of FCL.

One vehicle costs $150 to $700.
A functional swarm costs $15,000 to $70,000.

Components per vehicle include frame.
Components per vehicle include motors.
Components per vehicle include electronic speed controllers.
Components per vehicle include flight controller.
Components per vehicle include LED array.
Components per vehicle include battery.
Components per vehicle include communication module.

The frame holds everything.
Motors spin propellers.
Electronic speed controllers manage motor power.
The flight controller runs the stabilization algorithm.
The LED array creates the light show.
The battery stores energy.
The communication module receives formation commands.

A ground station sends commands.
The ground station runs the FCL encoder.
The encoder translates shape parameters into position commands.
Each vehicle receives its position.
The flight controller keeps the vehicle at that position.

GPS provides absolute position.
Real-Time Kinematic (RTK) GPS provides centimeter precision.
RTK requires a base station.
The base station costs $800.
It covers a five kilometer radius.

Safety systems must exist.
Geofencing prevents vehicles from leaving the area.
Return-to-home activates on signal loss.
Battery monitoring triggers landing at low charge.

The swarm operates at night.
LEDs are visible at altitude.
The formation is readable from the ground.
Formation duration is 20 to 60 minutes.

After the show vehicles return.
They land in a recovery zone.
A team collects them.
Batteries recharge.
Vehicles are checked.
The system is reusable.

The infrastructure cost is the ground station.
The ground station is one computer plus one radio.
The computer runs open source FCL software.
The radio communicates with the swarm.
Cost of ground station is $500.

Total system cost for a 100-vehicle swarm is $25,000 to $35,000.

See [050], [020], [000].

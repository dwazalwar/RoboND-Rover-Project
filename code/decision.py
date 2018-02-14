import numpy as np
from itertools import compress
from collections import defaultdict

# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function


def enable_stop(Rover):
    print('Stop enabled')
    # Set mode to "stop" and hit the brakes!
    Rover.throttle = 0
    # Set brake to stored brake value
    Rover.brake = Rover.brake_set
    Rover.mode = 'stop'
    Rover.vel = 0
    Rover.steer = 0
    return Rover


def fwd_mode(Rover):
    print('Forward mode')
    # Check the extent of navigable terrain
    if len(Rover.nav_angles) >= Rover.stop_forward:
        # If mode is forward, navigable terrain looks good
        # and velocity is below max, then throttle
        if Rover.vel < Rover.max_vel:
            # Set throttle value to throttle setting
            Rover.throttle = Rover.throttle_set
        else:  # Else coast
            Rover.throttle = 0
        Rover.brake = 0
        # Set steering to average angle clipped to the range +/- 15
        anglesD = [int(i * 180 / np.pi) for i in Rover.nav_angles]
        d = defaultdict(int)
        for i in anglesD:
            d[i] += 1

        result = max(d.items(), key=lambda x: x[1])
        maxValue = d[result[0]]
        angleArrayNew = {k: v for k, v in d.items() if v > 0.9 * maxValue and np.absolute(int(k) - result[0]) < 15}
        angleMin = min(angleArrayNew, key=lambda i: int(i))
        angleMax = max(angleArrayNew, key=lambda i: int(i))
        angleMean = (angleMin + angleMax) * 0.5

        a1 = min(d.items(), key=lambda x: x[1])
        a2 = max(d.items(), key=lambda x: x[1])
        angleRange = np.absolute(a1[0] - a2[0])
        print('angleRange = %s' % (angleRange))

        if angleRange > 75:
            steerAngle = np.mean(Rover.nav_angles) * 0.5 + np.max(Rover.nav_angles) * 0.5
            Rover.steer = np.clip(steerAngle, -15, 15)
        else:
            steerAngle = np.mean(Rover.nav_angles) * 0.75 + np.max(Rover.nav_angles) * 0.25
            Rover.steer = np.clip(steerAngle * 180 / np.pi, -15, 15)

        #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
    # If there's a lack of navigable terrain pixels then go to 'stop' mode
    elif len(Rover.nav_angles) < Rover.stop_forward:
        # Set mode to "stop" and hit the brakes!
        Rover = enable_stop(Rover)

    return Rover


def stop_mode(Rover):
    # If we're in stop mode but still moving keep braking
    if Rover.vel > 0.2:
        Rover.throttle = 0
        Rover.brake = Rover.brake_set
        Rover.steer = 0
    # If we're not moving (vel < 0.2) then do something else
    elif Rover.vel <= 0.2:
        # If we're stopped but see sufficient navigable terrain in front then go!
        if len(Rover.nav_angles) >= Rover.go_forward:
            # Set throttle back to stored value
            Rover.throttle = Rover.throttle_set
            # Release the brake
            Rover.brake = 0
            # Set steer to mean angle
            Rover.steer = np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15)
            Rover.mode = 'forward'

        # Now we're stopped and we have vision data to see if there's a path forward
        if len(Rover.nav_angles) < Rover.go_forward:
            Rover.throttle = 0
            # Release the brake to allow turning
            Rover.brake = 0
            # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
            Rover.steer = -15  # Could be more clever here about which way to turn
    return Rover


def stuck_mode(Rover):
    print('Rover seems stuck: reverse')
    Rover.throttle = -1
    Rover.brake = 0
    Rover.steer = 0
    if Rover.stuck_time > 2:
        Rover.steer = -90
        Rover.throttle = 0

    Rover.stuck_time -= 1
    if Rover.stuck_time <= 0 or len(Rover.nav_angles) > 2 * Rover.go_forward:
        print('Rover out of stuck mode')
        Rover.stuck_time = 0
        Rover.mode = 'stop'

    return Rover


def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        print('Length of Navigation: %s' % (len(Rover.nav_angles)))
        print('Rover mode is %s' % (Rover.mode))
        # Check for Rover.mode status
        if Rover.vel <= 0 and Rover.throttle > 0 and Rover.mode == "forward":
            Rover.stuck_time += 1
            if Rover.stuck_time > 5:
                Rover.mode = "stuck"

        if Rover.mode == 'stuck':
            Rover = stuck_mode(Rover)
        elif Rover.mode == 'forward':
            Rover = fwd_mode(Rover)
        else:
            Rover = stop_mode(Rover)

    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True

    return Rover

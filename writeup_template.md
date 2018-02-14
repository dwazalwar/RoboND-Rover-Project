## Project: Search and Sample Return

[image]: ./misc/rover_image.jpg
![alt text][image]

## Notebook Analysis ##
This notebook contains the functions from the lesson and provides the scaffolding that we need to test out mapping methods.

### Color Thresholding: ###

Every image from Rover camera has 3 possible areas namely ground area or navigation terrain, obstacles and in some images, we have rock samples too. Color thresholding is used to get masks showing pixel locations for each of them. It is important to select threshold values in such a way, that overlap between these 3 regions is minimal in masks as they will decide finally how accurately Rover is able to navigate. Using interactive Matplotlib tool, threshold values for navigation terrain and rock samples were selected. Obstacle map was obtained by simply reversing navigation terrain map. Following are the values selected for the thresholds.

Navigation Terrain = (160, 160, 160)
Rock Samples Threshold = (100,100,50)

Images shown below in Figure 1. display each individual maps for one such Rover camera image

[image_1]: ./misc/ColorThresholding.png
![alt text][image_1]
### Figure 1. Color Thresholding ###

### Process_Image Function: ###

This function basically processes an image from Rover camera, computes map for navigable terrain, obstacle, and rocks (if any) and finally prepares a mosaic image with all 3 areas mapped in a different color.

The first step is to perform a perspective transform on given image from Rover's camera and get it transformed to one where we are looking at the scene from top-down viewpoint. In unity simulator, we have reference grid defined where each grid cell represents 1 sq m on the ground. We select 4 source points in Rover's camera view and also then for same grid cell we define our destination points in top-down view too. In OpenCV then we use getPerspectiveTransform and warpPerspective to get our transform.

After perspective transform, for each image, we use color thresholding on warped images to get masks for navigation terrain, obstacle and rock samples. The navigable map received after color thresholding needs to be converted back to Rover coordinate form. While doing this, calculations are performed keeping in mind Rover will be at the center bottom of the image.

Figure 2. shows some of these steps just explained above.

[image_2]: ./misc/CoordinateTransformation.png
![alt text][image_2]
### Figure 2. Coordinate Transformation ###

Finally, we want to convert these navigation points in world coordinates to get an overall picture of the environment and also to find the quality of our Rover area mapping. We get 3 world maps one each for navigation, rocks and also obstacle. All these 3 maps are then used to update data.worldmap using different colors to generate a video output.

## Autonomous Navigation and Mapping ##

### Perception ###
perception_step() function is very similar to process_image from notebook analysis and has only 2 more additional details added.

In case of perspective transform, it is not necessarily correct every time and it is important to define this validity condition to improve the fidelity of the output. Mostly whenever roll and pitch angles are near zero, only those cases should be considered. However, we cannot use absolute zero too as then Rover will not navigate most of the time and mapped area will be very less. After careful experimental analysis, only positive pitch and roll angles with a tolerance of 0.5 degrees were considered valid for mapping.

Another addition is finally we convert navigable area points to polar coordinate form. This is needed in decision step to find navigable direction for Rover and find a suitable path for Rover to move.

### Decision ###
After defining perception pipeline, we now have to use information from it and define our Rover steering. Decision step mainly has 3 possible scenarios: Forward, Stop and Stuck. To control overall Rover behavior, we modify its throttle, brake and steer setting.

In Forward step, we know Rover has sufficient navigable terrain in front of it and the main task now is to find steering direction for Rover to move. We can use average angle obtained from our navigation points as one of possible steering angle. However, during the run, I found many times Rover keeps moving in a same circular area and also does not cover a good ground area. To make Rover more wall tracking, I have used an average of max and mean angles from navigation points. This helped to avoid those circular loops and also improved ground coverage. While navigating, we constantly keep track of the amount of terrain available in front, whenever we find it to be below the certain allowed threshold, we enable stop case and allow Rover to reorient itself. During forward motion, we usually set throttle to its allowed throttle_value and brake is released by setting it to 0.

In Stop case, we know Rover does not have enough navigable terrain in front of it. We now keep changing its steer angle by +/- 15 degrees until it has crossed the navigation terrain threshold to make Rover move again. During the stop, we set brake and throttle to 0. Once we have enough terrain in front of Rover, we enable forward motion again.

Sometimes I found Rover can get stuck. Therefore I added another set of conditions to get it out from such cases. Mainly we do this by setting throttle in a negative direction and also by changing steer angles. It takes time but once it gets off the obstacle area, we enable forward motion again.

## Results ##

Using above code changes and running Rover in a screen resolution of 1024 x 768 with Good graphics setting, I was able to get 96% environment mapped with a fidelity of around 76%. I was also able to locate all 6 rock samples in my final world map.

## Future Enhancements ##

As seen in the video of Rover run, there is still some room for additional improvements.

Firstly, Rover navigation is still not smooth as I would like to have. 2-3 times it got stuck and took some time to get out of it. This needs to be avoided and care should be taken while getting steering direction.

Secondly, I have not implemented yet picking of Rock samples part. I will be supporting this aspect later.









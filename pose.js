#!/usr/bin/env node

'use strict';

require('@tensorflow/tfjs-node-gpu')
//import * as posenet from '@tensorflow-models/posenet';

const posenet = require('@tensorflow-models/posenet')
const rs2 = require('./node_modules/node-librealsense/index.js');
const {GLFWWindow} = require('./node_modules/node-librealsense/examples/glfw-window.js');
const {glfw} = require('./node_modules/node-librealsense/examples/glfw-window.js');

const net = posenet.load();

const imageScaleFactor = 0.50;
const flipHorizontal = false;
const outputStride = 16;
// const imageElement = document.getElementById('cat');

// A GLFW Window to display the captured image
const win = new GLFWWindow(1280, 720, 'Node.js Capture Example');

// The main work pipeline of camera
const pipeline = new rs2.Pipeline();

// Start the camera
pipeline.start();

while (! win.shouldWindowClose()) {
  const frameset = pipeline.waitForFrames();
  // Paint the images onto the window
  win.beginPaint();
  const color = frameset.colorFrame;
  glfw.draw2x2Streams(win.window, 1,
      color.data, 'rgb8', color.width, color.height);
  win.endPaint();
  const pose = net.estimateSinglePose(color, imageScaleFactor, flipHorizontal, outputStride);
}

pipeline.stop();
pipeline.destroy();
win.destroy();
rs2.cleanup();

// load the posenet model
// const net = await posenet.load();
// const pose = await net.estimateSinglePose(imageElement, scaleFactor, flipHorizontal, outputStride);

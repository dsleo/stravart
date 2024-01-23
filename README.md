# Strava Art

Ultimate goal is to design routes as the contour of an image.

## How this (should) work
Here is the recipe:

1. Extract a contour (list of coordinates) from an image
2. Project that contour on a map.
3. Find the closests *feasible* (cycling or walking) points for each pair of coordinates.
4. Get direction between successives points.

We try to look for the best possible route by:
1. Applying multiple operations to the polygon (dilatation, rotation)
2. Measure each feasible route quality - as the total difference area between the image contour and the suggested polygon.
3. Select the best one according to the previous criterion.

## Installation

To install StravArt, follow these steps:

1. Clone the repository to your local machine

```bash
git clone https://github.com/yourusername/StravArt.git
cd StravArt
```

2. Create a virtual env

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies 
```bash
pip install -r requirements.txt
```

## Get Started

Have a look at the starter notebook.

## TODO

- [X] Start with a meta-heuristic to speed up search.
- [X] Add the openCV's find contour method. Something like this ?
- [ ] Approximate contours to have less points with `cv2.approxPolyDP` ? Unless we need more points to better constraint the feasible route (see [issue](https://github.com/dsleo/stravart/issues/1))?

- [ ] Write the route to gpx file.
    
- [X] Add LLM Option "Give me the contour of a crocodile" (it's a huge fail ;) )
- [ ] Try multi-modal LLM maybe ¯\\\_(ツ)\_/¯






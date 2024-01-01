# Strava Art

Ultimate goal is to design routes as the contour of an image.

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

- [ ] Be smart and craft a nice meta-heuristic to speed up search.
- [ ] Add the openCV's find contour method. Something like this ?

```python
r = rgb2gray(io.imread(img_path))
r = exposure.adjust_gamma(r, 0.5)
contours = measure.find_contours(r, 0.9)

contours_paths = [c for n, c in enumerate(contours)]
longest_contour = max(contours_paths, key=len)
```

- [ ] Write the route to gpx file.
- [ ] Add LLM Option "Give me the contour of a crocodile"
- [ ] Ask LLM directly "Give me directions that makes the contour of a crocodile" ?
- [ ] Try multi-modal LLM maybe ¯\\\_(ツ)\_/¯






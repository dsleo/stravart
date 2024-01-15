from dataclasses import dataclass
import cv2
import numpy as np
import urllib.request
import matplotlib.pyplot as plt

@dataclass
class ContourExtractor():
    image_path: str
    image: np.ndarray = None
    merged_contour: bool = False
    contours: list = None

    def _read_image(self):
        if self.image_path.startswith("http"):
            response = urllib.request.urlopen(self.image_path)
            image_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
            self.image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        else:
            self.image = cv2.imread(self.image_path)

        if self.image is None:
            raise ValueError("Could not open or find the image")
    
    def get_contours(self, show=False, merge=True):
        """Extract contours from an image and merge them if they share points"""
        self._read_image()

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        #inch'allah those params works generically
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        edged = cv2.Canny(blurred, 10, 100)

        # Find contours using full hierarchy
        contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if merge:
            self.merged_contour = True
            self.contours = self.merge_contours(contours)
        else:
            self.merged_contour = False
            self.contours = contours

        if show:
            self.plot_contours()

        return self.contours

    def merge_contour(self, contour_ix, threshold=0.05):
        """Merge contours closer than threshold (relative to image size) to contour_ix contour"""
        if threshold < 0 or threshold > 1:
            raise ValueError("Threshold is between 0 and 1.")

        if not self.merged_contour:
            raise ValueError("You need to get contours first!")

        if contour_ix not in range(len(self.contours)):
            raise ValueError("Contour_ix is higher than the number of contours.")

        img_threshold = threshold * min(self.image.shape[:2])

        contour = self.merge_contours_from_specific(self.contours, contour_ix, threshold=img_threshold)

        return contour

    def plot_contours(self):
        cv2.drawContours(self.image, self.contours, -1, (0, 255, 0), 2)
        image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        plt.imshow(image_rgb)
        plt.show()

    @staticmethod
    def contours_share_point(contour1, contour2):
        return any(np.any(np.all(point == contour2, axis=2)) for point in contour1)

    @staticmethod
    def min_distance(contour1, contour2):
        c1 = contour1.reshape(-1, 2)
        c2 = contour2.reshape(-1, 2)
        return np.min([np.linalg.norm(x - y) for x in c1 for y in c2])

    @staticmethod
    def merge_contours(contours):
        """Merge contours that share elements."""
        n = len(contours)
        parent = [i for i in range(n)]
        rank = [0] * n

        # Merge contours with shared points
        for i in range(n):
            for j in range(i + 1, n):
                if ContourExtractor.contours_share_point(contours[i], contours[j]):
                    ContourExtractor.union(parent, rank, i, j)

        # Merge contours in the same set
        merged_contours = {}
        for i in range(n):
            idx = ContourExtractor.find(parent, i)
            merged_contours.setdefault(idx, []).append(contours[i])

        return [np.vstack(merged) for merged in merged_contours.values()]

    @staticmethod
    def get_contours_distance(contours):
        num_contours = len(contours)
        contour_distances = np.zeros((num_contours, num_contours))
        for i in range(num_contours):
            for j in range(i + 1, num_contours):  # Start from i+1 to avoid self-comparison
                distance = ContourExtractor.min_distance(contours[i], contours[j])
                contour_distances[i, j] = distance
                contour_distances[j, i] = distance
        return contour_distances

    @staticmethod
    def merge_contours_from_specific(contours, contour_ix, threshold=0.05):
        n = len(contours)
        if n <= 1 or contour_ix >= n:
            return contours

        start_contour = contours[contour_ix]
        merged_contours = [start_contour]

        # Function to merge contours based on distance to the start contour
        def should_merge_with_start(contour):
            return ContourExtractor.min_distance(start_contour, contour) < threshold

        # Merge contours that are close to the start contour
        for i, contour in enumerate(contours):
            if i != contour_ix and should_merge_with_start(contour):
                merged_contours.append(contour)

        # Combine all merged contours into one
        final_contour = np.vstack(merged_contours)

        return final_contour

    @staticmethod
    def find(parent, i):
        if parent[i] == i:
            return i
        return ContourExtractor.find(parent, parent[i])

    @staticmethod
    def union(parent, rank, x, y):
        xroot = ContourExtractor.find(parent, x)
        yroot = ContourExtractor.find(parent, y)

        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot
        else:
            parent[yroot] = xroot
            rank[xroot] += 1

    def merge_largest_contour(self, threshold):
        if not self.merged_contour:
            raise ValueError("You need to get contours first!")
        else:
            contour_ix  = max(range(len(self.contours)), key=lambda i: len(self.contours[i]))
            return self.merge_contour(contour_ix=contour_ix, threshold=threshold)
        
    
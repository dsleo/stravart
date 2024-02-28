from dataclasses import dataclass
import numpy as np
import cv2

@dataclass
class Contour:
    raw_contour: np.ndarray

    def approximate(self, eps=0.0001):
        self.merged_contour = self.raw_contour.reshape(-1, 2)
        epsilon = eps * cv2.arcLength(self.merged_contour, True)
        self.simplified_contour = cv2.approxPolyDP(self.merged_contour, epsilon, True)

    def filter_close_points(self, threshold):
        contour = self.simplified_contour.reshape(-1, 2)
        if len(contour) == 0:
            return np.array([])

        filtered_contour = [contour[0]]
        for point in contour[1:]:
            if all(np.linalg.norm(point - other_point) >= threshold for other_point in filtered_contour):
                filtered_contour.append(point)

        return Contour(raw_contour=np.array(filtered_contour))

    def replace_with_longest_sublist(self, contour):
        contour_tuples = [tuple(point) for point in contour]
        longest_sublists = {}

        for i in range(len(contour_tuples)):
            for j in range(i + 1, len(contour_tuples)):
                start_point = contour_tuples[i]
                end_point = contour_tuples[j]
                sublist = contour_tuples[i:j + 1]

                if (start_point, end_point) not in longest_sublists or len(sublist) > len(longest_sublists[(start_point, end_point)]):
                    longest_sublists[(start_point, end_point)] = sublist

        new_contour = []
        i = 0
        while i < len(contour_tuples):
            for j in range(i + 1, len(contour_tuples) + 1):
                start_point = contour_tuples[i]
                end_point = contour_tuples[j - 1]
                if (start_point, end_point) in longest_sublists:
                    new_contour.extend(longest_sublists[(start_point, end_point)])
                    i = j - 1
                    break
            i += 1

        return np.array(new_contour)
    
    def slice_contour(self, step: int):
        """Returns a new Contour instance with raw_contour sliced by the given step."""
        sliced = self.raw_contour[::step]
        return Contour(raw_contour=sliced)
    
    def __delitem__(self, index: int):
        """Delete an element from raw_contour at the specified index."""
        self.raw_contour = np.delete(self.raw_contour, index, axis=0)

    def close(self):
        """Ensure the contour is closed by making the first point the same as the last point."""
        if not np.array_equal(self.raw_contour[0], self.raw_contour[-1]):
            self.raw_contour = np.vstack([self.raw_contour, self.raw_contour[0]])

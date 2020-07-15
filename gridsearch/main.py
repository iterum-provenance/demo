import cv2
import numpy as np

if __name__ == "__main__":
    input_files = [
        "../../demo-cats/cats_subset/cat.1.jpg",
        "../../demo-cats/cats_subset/cat.2.jpg",
        "../../demo-cats/cats_subset/cat.3.jpg",
        "../../demo-cats/cats_subset/cat.4.jpg",
        "../../demo-cats/cats_subset/cat.5.jpg",
        "../../demo-cats/cats_subset/cat.6.jpg",
        "../../demo-cats/cats_subset/cat.7.jpg",
        "../../demo-cats/cats_subset/cat.8.jpg",
        "../../demo-cats/cats_subset/cat.9.jpg",
        "../../demo-cats/cats_subset/cat.10.jpg",
    ]
    input_files = [input_files[0]]
    results = []
    for photo_path in input_files:
        img = cv2.imread(photo_path, 0)

            # Perform edge detection
        edges = cv2.Canny(img, 200, 500)

        # Perform edge detection

        cimg = edges
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1,20,
                param1=50, param2=30, minRadius=0, maxRadius=0)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for circle in circles:
                cv2.circle(cimg,(circle[0],circle[1]),2,(0,0,255),3) # Draw the center
                cv2.circle(cimg,(circle[0],circle[1]),circle[2],(0,255,0),2) # Draw the radius
        # results.append(cimg)

        cv2.imshow("output", np.hstack([img, edges, cimg]))
        cv2.waitKey(0)
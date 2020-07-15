import cv2
import numpy as np
import math 
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
    input_files = input_files[0:1]
    results = []
    for photo_path in input_files:
        img = cv2.imread(photo_path, 1)

        # Perform edge detection    
        blurred_img = cv2.medianBlur(img,5)
        
        edges = cv2.Canny(blurred_img, 150, 350)

        # Perform hough transform

        cimg = img.copy()
        print(cimg.shape)
        max_radius = int(cimg.shape[0] / 4)
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20,
                param1=30, param2=25, minRadius=0, maxRadius=max_radius)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            print(len(circles))
            for circle in circles:
                print(circle)
                cv2.circle(cimg,(circle[0],circle[1]),2,(0,0,255),3) # Draw the center
                cv2.circle(cimg,(circle[0],circle[1]),circle[2],(0,255,0),2) # Draw the radius
        # results.append(cimg)

        cv2.imshow("output", np.hstack([edges]))
        cv2.waitKey(0)
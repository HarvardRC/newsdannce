import cv2
import os

def avi_to_jpg(avi_file_path, output_folder):
    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Capture the video from the file
    cap = cv2.VideoCapture(avi_file_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()  # Read the frame
        if not ret:
            break  # Break the loop if there are no frames left

        # Construct filename for each frame
        output_path = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(output_path, frame)  # Save the frame as JPEG file
        frame_count += 1

    cap.release()  # Release the video capture object
    print(f"Frames saved: {frame_count}")

# Example usage
# base_path = 'G:\\Videos\\6cam\\jn187\\2024_04_25_chris_test_mir_intrinsic\\intrinsics'
# for i in range(2,7):
#     if i == 4:
#         continue
#     vid_path = os.path.join(base_path, f"Camera{i}", "0.avi")
#     print(vid_path)
#     avi_to_jpg(vid_path, os.path.join(base_path,f"Camera{i}"))

avi_to_jpg("G:\\Videos\\6cam\\jn187\\2024_04_25_chris_test_mir_intrinsic\\intrinsics\\Camera6\\0.avi", "G:\\Videos\\6cam\\jn187\\2024_04_25_chris_test_mir_intrinsic\\intrinsics\\Camera6")

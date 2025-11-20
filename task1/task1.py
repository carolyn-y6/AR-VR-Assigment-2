"""
ELEC4547 Assignment 2 - VR Rendering Pipeline (Student Version)
Complete VR Display Simulation Pipeline

Pipeline Flow:
    Stereo Images -> Lens Distortion -> Chromatic Aberration -> Foveated Rendering -> VR Output

Requirements:
    pip install numpy matplotlib pillow scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
from scipy.ndimage import gaussian_filter
import math


class VRPipeline:
    """Complete VR rendering pipeline - implement all stages"""

    def __init__(self, left_img_path, right_img_path):
        """
        Initialize the VR pipeline with stereo image pair

        Args:
            left_img_path: Path to left eye image
            right_img_path: Path to right eye image
        """
        print("Initializing VR Pipeline...")

        # TODO: Load the stereo images using PIL
        # Hint: Use Image.open() and convert to numpy array
        left_pil = Image.open(left_img_path)
        right_pil = Image.open(right_img_path)

        self.left_img = np.array(left_pil)
        self.right_img = np.array(right_pil)

        # Get image dimensions
        self.height, self.width = self.left_img.shape[:2]

        # Set gaze point at center (for foveated rendering)
        self.gaze_x = self.width // 2
        self.gaze_y = self.height // 2

        print(f"Loaded stereo pair: {self.width}x{self.height}")
        print(f"Gaze point: ({self.gaze_x}, {self.gaze_y})\n")

    def apply_lens_distortion(self, img, k1=0.25, k2=0.15, save_output=True):
        """
        Apply barrel distortion to simulate VR lens optics

        This simulates the pincushion-to-barrel distortion correction needed
        for VR lenses. Real VR headsets apply this in reverse to pre-distort
        the image so that it looks correct through the curved lenses.

        Args:
            img: Input image (H x W x 3)
            k1: First radial distortion coefficient (primary effect)
            k2: Second radial distortion coefficient (secondary effect)
            save_output: Whether to save the output image

        Returns:
            Distorted image with barrel effect

        Implementation hints:
            - Use Brown-Conrady distortion model: r' = r * (1 + k1*r^2 + k2*r^4)
            - Normalize coordinates relative to image center
            - For each output pixel, find where it maps in the input image
            - Use coordinate mapping and interpolation (or nearest neighbor)
            - Remember to handle boundary cases (pixels mapping outside image)
        """
        print("Applying lens distortion...")

        h, w = img.shape[:2]
        # TODO: Implement barrel distortion
        # Step 1: Create output image and coordinate grids
        # Step 2: Normalize coordinates (center at origin, range [-1, 1])
        # Step 3: Calculate radius from center
        # Step 4: Apply distortion formula
        # Step 5: Map back to pixel coordinates
        # Step 6: Sample from input image (handle boundaries)

        distorted = np.zeros_like(img)

        # Your implementation here
        center_x = (w) / 2
        center_y = (h) / 2
        d = int(min(w, h) / 2)

        for y in range(h):
            for x in range(w):
                # Calculate the distance from the center

                dx = (x - center_x) / center_x
                dy = (y - center_y) / center_y
                r = math.sqrt(dx**2 + dy**2)
                radial_distortion = r * (1 + k1*r**2 + k2*r**4) 
                #tangential_distortion_x = 2 * p1 * dx * dy + p2 * (r**2 + 2 * dx**2)
                #tangential_distortion_y = p1 * (r**2 + 2 * dy**2) + 2 * p2 * dx * dy
                distorted_x = int(center_x + center_x *(dx * radial_distortion ))
                distorted_y = int(center_y + center_y *(dy * radial_distortion ))

                # Check if the distorted coordinates are within the image bounds
                if 0 <= distorted_x < w and 0 <= distorted_y < h:
                    # Set the pixel color at (x,y) to the color of the distorted pixel at (distorted_x,distorted_y)
                    distorted[y][x] = img[distorted_y][distorted_x]
        # Convert the distorted image back to uint8
        distorted_img = distorted.astype(np.uint8)

        self.distorted_img = distorted_img

        
        # ...

        # Save output if requested
        if save_output and distorted is not None and distorted.size > 0:
            output_path = "lens_distortion_output.png"
            Image.fromarray(distorted).save(output_path)
            print(f"  -> Saved output: {output_path}")

        print(f"  -> Applied barrel distortion (k1={k1}, k2={k2})")
        return distorted

    def apply_chromatic_aberration(
        self, img, r_scale=1.01, g_scale=1.0, b_scale=0.99, save_output=True
    ):
        """
        Apply chromatic aberration to simulate lens color fringing

        Real lenses refract different wavelengths differently, causing color
        channels to focus at slightly different distances. This creates colored
        fringes, especially near edges and at image periphery.

        Args:
            img: Input image (H x W x 3)
            r_scale: Red channel scaling factor (>1.0 means expand outward)
            g_scale: Green channel scaling factor (typically 1.0 as reference)
            b_scale: Blue channel scaling factor (<1.0 means contract inward)
            save_output: Whether to save the output image

        Returns:
            Image with chromatic aberration effect

        Implementation hints:
            - Process each RGB channel separately
            - Scale coordinates from center differently for each channel
            - Red typically expands outward, blue contracts inward
            - Use coordinate transformation: x' = (x - cx) * scale + cx
            - Interpolate or use nearest neighbor for sampling
            - Clip coordinates to image boundaries
        """
        print("Applying chromatic aberration...")

        h, w = img.shape[:2]
        # TODO: Implement chromatic aberration
        # Step 1: Create output image
        # Step 2: Find image center
        # Step 3: For each color channel (R, G, B):
        #         - Scale coordinates differently
        #         - Sample from input at scaled positions
        # Step 4: Combine channels

        result = np.zeros_like(img)

        # Your implementation here
        center_x = w / 2
        center_y = h / 2
        d = int(min(w, h) / 2)

        # Iterate through each pixel in the image
        for y in range(h):
            for x in range(w):
                # Calculate distance from the center
                dx, dy = x - center_x, y - center_y
                
                # Red channel (expand outward)
                rx, ry = int(dx * r_scale + center_x), int(dy * r_scale + center_y)
                if 0 <= rx < w and 0 <= ry < h:
                    result[y, x, 0] = img[ry, rx, 0]

                # Green channel (no change)
                gx, gy = int(dx * g_scale + center_x), int(dy * g_scale + center_y)
                if 0 <= gx < w and 0 <= gy < h:
                    result[y, x, 1] = img[gy, gx, 1]

                # Blue channel (contract inward)
                bx, by = int(dx * b_scale + center_x), int(dy * b_scale + center_y)
                if 0 <= bx < w and 0 <= by < h:
                    result[y, x, 2] = img[by, bx, 2]

        # Save output if requested
        if save_output and result is not None and result.size > 0:
            output_path = "chromatic_aberration_output.png"
            Image.fromarray(result).save(output_path)
            print(f"  -> Saved output: {output_path}")

        print(
            f"  -> Applied chromatic aberration (R={r_scale}, G={g_scale}, B={b_scale})"
        )
        return result

    def apply_foveated_rendering(
            self, img, inner_radius=100, outer_radius=250, save_output=True
    ):
        """
        Apply foveated rendering - blur peripheral vision to save computation

        Human eyes have high resolution only in the center (fovea). VR systems
        exploit this by rendering peripheral areas at lower quality. This can
        improve performance by 3-5x in real systems.

        Args:
            img: Input image (H x W x 3)
            inner_radius: Radius of sharp central region (pixels)
            outer_radius: Radius where blur reaches maximum (pixels)
            save_output: Whether to save the output image

        Returns:
            Image with peripheral blur applied
        """
        print("Applying foveated rendering...")

        h, w = img.shape[:2]

        # Step 1: Calculate distance from each pixel to gaze point
        # Use center
        gaze_x = getattr(self, 'gaze_x', w // 2)
        gaze_y = getattr(self, 'gaze_y', h // 2)

        # Create coordinate grids for distance calculation
        y_coords, x_coords = np.ogrid[:h, :w]
        dist_from_gaze = np.sqrt((x_coords - gaze_x) ** 2 + (y_coords - gaze_y) ** 2)

        # Step 2: Compute blur strength based on distance
        max_sigma = 10.0  # Maximum blur strength
        blur_mask = np.zeros_like(dist_from_gaze, dtype=np.float32)
        blur_mask[dist_from_gaze <= inner_radius] = 0.0
        blur_mask[dist_from_gaze > outer_radius] = 1.0

        in_transition = (dist_from_gaze > inner_radius) & (dist_from_gaze <= outer_radius)
        blur_mask[in_transition] = (dist_from_gaze[in_transition] - inner_radius) / (outer_radius - inner_radius)

        # Step 3: Create blurred versions of the image (different sigma values)
        from scipy.ndimage import gaussian_filter

        # Create blur levels
        num_blur_levels = 3
        blurred_versions = []

        # Original image (no blur)
        original_float = img.astype(np.float32)
        blurred_versions.append(original_float)

        # Create progressively more blurred versions
        for i in range(1, num_blur_levels):
            sigma = (i / (num_blur_levels - 1)) * max_sigma
            blurred_img = np.zeros_like(original_float)

            # Apply Gaussian blur to each channel separately
            for channel in range(3):
                blurred_img[..., channel] = gaussian_filter(
                    original_float[..., channel],
                    sigma=sigma
                )
            blurred_versions.append(blurred_img)

        # Step 4: Blend based on distance (sharp in center, blurred at edges)

        result = img.copy().astype(np.float32)

        # Your implementation here
        # ...

        # Save output if requested
        result_uint8 = result.astype(np.uint8)
        if save_output and result_uint8 is not None and result_uint8.size > 0:
            output_path = "foveated_rendering_output.png"
            Image.fromarray(result_uint8).save(output_path)
            print(f"  -> Saved output: {output_path}")

        return result_uint8

    def render_pipeline(self, output_dir="."):
        """
        Execute the complete VR rendering pipeline

        This function chains all VR effects together to simulate what a real
        VR headset does to render the final image seen by the user.

        Pipeline stages:
            1. Load stereo images (left and right eye views)
            2. Apply lens distortion (correct for VR optics)
            3. Apply chromatic aberration (simulate lens color fringing)
            4. Apply foveated rendering (optimize peripheral vision)

        Returns:
            Tuple of (left_final, right_final) processed images
        """
        print("\n" + "=" * 70)
        print("VR RENDERING PIPELINE")
        print("=" * 70 + "\n")

        # Stage 1: Get stereo pair
        print("Stage 1: Loading stereo images...")
        left_raw = self.left_img.copy()
        right_raw = self.right_img.copy()
        print(f"  -> Loaded left: {left_raw.shape}")
        print(f"  -> Loaded right: {right_raw.shape}\n")

        # Stage 2: Apply lens distortion to both eyes
        print("Stage 2: Processing LEFT eye...")
        left_distorted = self.apply_lens_distortion(left_raw, k1=0.25, k2=0.15)

        print("\nStage 2: Processing RIGHT eye...")
        right_distorted = self.apply_lens_distortion(right_raw, k1=0.25, k2=0.15)

        # Stage 3: Apply chromatic aberration
        print("\nStage 3: Applying chromatic aberration...")
        left_chromatic = self.apply_chromatic_aberration(
            left_distorted, r_scale=1.01, g_scale=1.0, b_scale=0.99
        )
        right_chromatic = self.apply_chromatic_aberration(
            right_distorted, r_scale=1.01, g_scale=1.0, b_scale=0.99
        )

        # Stage 4: Apply foveated rendering
        print("\nStage 4: Applying foveated rendering...")
        left_final = self.apply_foveated_rendering(
            left_chromatic, inner_radius=100, outer_radius=250
        )
        right_final = self.apply_foveated_rendering(
            right_chromatic, inner_radius=100, outer_radius=250
        )

        # Save visualization
        print("\nSaving results...")
        self._save_results(left_raw, right_raw, left_final, right_final, output_dir)

        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)
        print("\nPipeline stages:")
        print("  1. Stereo images    -> Original left/right eye views")
        print("  2. Lens distortion  -> Barrel distortion for VR optics")
        print("  3. Chromatic aberr. -> RGB channel separation effect")
        print("  4. Foveated render  -> Peripheral blur for performance")
        print("\nThis is how real VR headsets process images!\n")

        return left_final, right_final

    def _save_results(self, left_raw, right_raw, left_final, right_final, output_dir):
        """
        Save pipeline visualization showing before/after comparison

        Creates two output images:
            1. 2x2 grid showing original vs. processed
            2. Side-by-side final output (simulating VR headset view)
        """

        # Create comparison grid (2x2: original vs. final for both eyes)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            "VR Pipeline: Original vs. Processed", fontsize=16, fontweight="bold"
        )

        # Original images
        axes[0, 0].imshow(left_raw)
        axes[0, 0].set_title("LEFT Eye - Original", fontsize=12, fontweight="bold")
        axes[0, 0].axis("off")

        axes[0, 1].imshow(right_raw)
        axes[0, 1].set_title("RIGHT Eye - Original", fontsize=12, fontweight="bold")
        axes[0, 1].axis("off")

        # Processed images with gaze point marked
        axes[1, 0].imshow(left_final)
        axes[1, 0].plot(
            self.gaze_x, self.gaze_y, "r+", markersize=15, markeredgewidth=2
        )
        axes[1, 0].set_title(
            "LEFT Eye - Processed\n[Distortion + Chromatic + Foveated]",
            fontsize=12,
            fontweight="bold",
        )
        axes[1, 0].axis("off")

        axes[1, 1].imshow(right_final)
        axes[1, 1].plot(
            self.gaze_x, self.gaze_y, "r+", markersize=15, markeredgewidth=2
        )
        axes[1, 1].set_title(
            "RIGHT Eye - Processed\n[Distortion + Chromatic + Foveated]",
            fontsize=12,
            fontweight="bold",
        )
        axes[1, 1].axis("off")

        plt.tight_layout()
        output_path = os.path.join(output_dir, "vr_pipeline_comparison.png")
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  -> Saved: {output_path}")

        # Create side-by-side final output (like VR headset view)
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle("Final VR Output (Side-by-Side)", fontsize=14, fontweight="bold")

        # Left eye
        axes[0].imshow(left_final)
        axes[0].set_title("LEFT EYE", fontsize=12, fontweight="bold")
        axes[0].plot(self.gaze_x, self.gaze_y, "r+", markersize=20, markeredgewidth=3)
        # Draw arrow to gaze point using keyboard symbols
        axes[0].text(
            self.gaze_x + 30,
            self.gaze_y,
            "<-- Gaze",
            color="red",
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )
        axes[0].axis("off")

        # Right eye
        axes[1].imshow(right_final)
        axes[1].set_title("RIGHT EYE", fontsize=12, fontweight="bold")
        axes[1].plot(self.gaze_x, self.gaze_y, "r+", markersize=20, markeredgewidth=3)
        axes[1].text(
            self.gaze_x + 30,
            self.gaze_y,
            "<-- Gaze",
            color="red",
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )
        axes[1].axis("off")

        plt.tight_layout()
        output_path = os.path.join(output_dir, "vr_final_output.png")
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  -> Saved: {output_path}")


###############################################################################
# MAIN PROGRAM
###############################################################################


def main():
    """
    Main function to run the VR pipeline demo

    Instructions:
        1. Implement the three core functions:
            - apply_lens_distortion()
            - apply_chromatic_aberration()
            - apply_foveated_rendering()

        2. Test your implementation by running this script

        3. Compare your output with the reference images

        4. Adjust parameters to understand their effects
    """
    print("\n" + "=" * 70)
    print("ELEC4547 - VR Rendering Pipeline (Student Version)")
    print("=" * 70)
    print("\nThis demo integrates all VR effects into a complete pipeline:")
    print("  * Stereo images (left and right eye)")
    print("  * VR lens distortion")
    print("  * Chromatic aberration")
    print("  * Foveated rendering (performance optimization)")
    print("\n" + "=" * 70 + "\n")

    # Set up image paths
    base_path = os.path.dirname(os.path.abspath(__file__))
    left_path = os.path.join(base_path, "./data/left.jpg")
    right_path = os.path.join(base_path, "./data/right.jpg")

    # Check if images exist
    if not os.path.exists(left_path) or not os.path.exists(right_path):
        print(f"ERROR: Stereo images not found!")
        print(f"  Expected: {left_path}")
        print(f"            {right_path}")
        print("\nPlease make sure the stereo images are in the correct location.")
        return

    # Run the complete pipeline
    pipeline = VRPipeline(left_path, right_path)
    left_final, right_final = pipeline.render_pipeline()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  -> vr_pipeline_comparison.png  (before/after comparison)")
    print("  -> vr_final_output.png         (final VR headset view)")
    print("\nThese files show how real VR systems process images!")
    print("\nNext steps:")
    print("  1. Open the output images and examine the effects")
    print("  2. Try adjusting the distortion parameters (k1, k2)")
    print("  3. Experiment with chromatic aberration scales")
    print("  4. Change the foveated rendering radii")
    print("  5. Move the gaze point to see peripheral blur changes")
    print("\n")


if __name__ == "__main__":
    main() 

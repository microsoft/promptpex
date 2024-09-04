## Instructions for GPT:

### Objective:
Prompt the user for a message, generate a GIF that displays the message one letter at a time with random rainbow colors, and include a final graphic. The letters should display at a specific speed, and the final graphic should appear for a longer duration.

### Steps:

1. **Prompt the User for a Message**:
   - Ask the user to input the message they want to animate.
   - Confirm the message with the user before proceeding.

2. **Define Rainbow Colors**:
   - Use the following list of colors for the letters: red, orange, yellow, green, blue, indigo, violet.

3. **Generate Images for Each Letter**:
   - For each letter in the message (including spaces as blank frames), generate an image with the following characteristics:
     - Uppercase letters unless specified otherwise.
     - Random rainbow color, ensuring no two consecutive letters have the same color.
     - Bold sans-serif typography for Latin scripts.
     - Use a font that supports a wide range of Unicode characters to accommodate non-Latin scripts, such as “DejaVu Sans”.
     - Centered on a black background.
     - If the user asks for the X from Twitter, use the "Mathematical Double-Struck Capital X" character in Unicode, and its codepoint is U+1D54F.

4. **Generate the Final Graphic**:
   - Use DALL-E to generate a final graphic based on a kawaii theme appropriate for the context of the message.
   - Resize the final graphic to match the frame size of the letters.

5. **Create the GIF**:
   - Combine the letter images and the final graphic into an animated GIF.
   - Set the duration for each letter frame to 250 milliseconds.
   - Set the duration for the final graphic frame to 1000 milliseconds and display it twice for a total of 2000 milliseconds.
   - Include a blank frame after the final graphic to create a pause before the GIF loops.

6. **Output the GIF**:
   - Save the GIF and provide a download link to the user.

### Code Implementation:

\`\`\`python
from PIL import Image, ImageDraw, ImageFont
import imageio
import random
import requests
from io import BytesIO

def create_gif(message):
    # Define the rainbow colors
    rainbow_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    
    # Parameters for the text
    font_size = 150
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    width, height = 400, 400
    
    # Function to create an image with a single letter
    def create_image_with_letter(letter, color):
        img = Image.new('RGB', (width, height), "black")
        draw = ImageDraw.Draw(img)
        text_width, text_height = draw.textsize(letter, font=font)
        draw.text(
            ((width - text_width) / 2, (height - text_height) / 2),
            letter, font=font, fill=color
        )
        return img

    # Generate frames for the text
    frames = []
    previous_color = None
    for letter in message:
        if letter != " ":
            # Ensure no two consecutive letters have the same color
            color = random.choice(rainbow_colors)
            while color == previous_color:
                color = random.choice(rainbow_colors)
            previous_color = color
            img = create_image_with_letter(letter, color)
        else:
            # Create a blank frame for space
            img = Image.new('RGB', (width, height), "black")
        frames.append(img)

    # Generate the final graphic using DALL-E
    dalle_response = dalle.text2im({
        "prompt": f"A kawaii style graphic appropriate for the context of the message '{message}'",
        "size": "1024x1024",
        "n": 1
    })
    final_graphic_url = dalle_response['images'][0]['url']
    response = requests.get(final_graphic_url)
    final_graphic = Image.open(BytesIO(response.content)).resize((width, height))

    # Add the final graphic frame and a blank frame for pause
    frames.append(final_graphic)
    frames.append(final_graphic)
    blank_frame = Image.new('RGB', (width, height), "black")
    frames.append(blank_frame)

    # Save frames as a GIF with adjusted durations
    gif_path = "output.gif"
    frames[0].save(
        gif_path, save_all=True, append_images=frames[1:],
        duration=[250] * (len(frames) - 3) + [1000, 1000, 1000], loop=0
    )

    return gif_path

# Example usage:
message = input("Enter the message you want to animate: ")
gif_path = create_gif(message)
print(f"Animated GIF created successfully: {gif_path}")
\`\`\`

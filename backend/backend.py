import openai
import os
import subprocess
import re
from pathlib import Path
import tempfile
import time

from dotenv import load_dotenv
load_dotenv()


client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
   
from manim_examples import EXAMPLES  

def manim_gen_prompt(user_query):
    return (
        f"""
Create a Manim animation for the following math problem: {user_query}
Bash commands should be enclosed by ```bash ``` and python code should be enclosed by ```python ```


You should write a self-contained class that can then be run to create a short-explanatory video. Your generated code should have no issues with compilation or execution and should include any relevant imports.
Be super sure that the video doesn't include overlapping elements. If you run out of space, clear the screen.
Ensure all objects remain fully visible within the default frame. Center all objects and scale them if necessary. Consider using scale_to_fit_width and scale_to_fit_height to avoid writing stuff out of frame.
Feel free to incorporate the layout manager into your code.


Please include the bash command to run the script and the python code itself. In the bash command to render the code, choose a frame rate of 25.
Please make the command start with manim -ql --fps 15
"""
    )


def generate_manim_code(user_query):
    user_prompt = manim_gen_prompt(user_query)

    messages = [
        {
            "role": "system",
            "content": (
                "You output ONLY valid Manim CE Python code."
                "Use exactly one Scene class."
                "No backticks. No explanations. No comments."
                "Do NOT use axes.get_tangent_line. If you want a tangent, use TangentLine(graph, x0, length=..., color=...); otherwise, just don't show the tangent."
            ),
        },
    ]

    for example in EXAMPLES[:2]:
        messages.append({
            "role": "user",
            "content": example["user"],
        })
        messages.append({
            "role": "assistant",
            "content": example["code"],
        })

    # === Real user request ===
    messages.append({
        "role": "user",
        "content": user_prompt,
    })

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0,
        max_tokens=1500,
    )

    gpt_response = response.choices[0].message.content
    print("manim code:", gpt_response)
    print("\n\n")
    return gpt_response



def get_python_code(response: str) -> str:
    """
    Extracts the Python code block from a GPT response safely.
    Handles cases where the block is incomplete or missing closing backticks.
    """
    # Try to match a complete ```python ... ``` fenced block
    match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        code = match.group(1).strip()
        print("✅ Extracted complete Python code block.")
        return code

    # Fallback: handle open but unclosed ```python block
    if "```python" in response:
        start = response.index("```python") + len("```python")
        code = response[start:].strip()
        print("⚠️ Warning: Detected unclosed Python code block — using partial content.")
        return code

    # Final fallback: try detecting bare Python class/def if model didn’t fence
    match = re.search(r"(class\s+\w+\(.*?\):.*)", response, re.DOTALL)
    if match:
        code = match.group(1).strip()
        print("⚠️ Warning: No code fence found — extracted from text heuristically.")
        return code

    raise Exception("❌ No valid Python code found in GPT response.")

def get_manim_command(response: str):
    """
    Extracts the Manim bash command (like 'manim -pql file.py SceneName')
    from the GPT response safely, even if formatting is inconsistent.
    """
    # First try fenced code block
    match = re.search(r"```bash\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        command = match.group(1).strip()
        print(f"✅ Extracted Manim command: {command}")
        return command

    # Fallback: search for 'manim ' line in plain text
    match = re.search(r"manim\s+[^\n]+", response)
    if match:
        command = match.group(0).strip()
        print(f"⚠️ Extracted Manim command (fallback): {command}")
        return command

    raise Exception("❌ No valid Manim command found in GPT response.")


def generate_manim_video(code: str, command: str, output_dir="outputs"):
    """
    Generates a Manim video from code and command, saves it in output_dir,
    and returns the path to the generated MP4.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Create temporary Python file
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp_file:
        tmp_file.write(code.encode("utf-8"))
        tmp_filename = tmp_file.name

    # 2. Replace the filename in the Manim command
    parts = command.split()
    for i, p in enumerate(parts):
        if p.endswith(".py"):
            parts[i] = tmp_filename

    # 3. Run the Manim CLI command
    try:
        subprocess.run(parts, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("❌ Manim render failed:")
        print(e.stderr)
        return None

    # 4. Move the generated video to output_dir
    # Find the only .mp4 in the Manim media/videos folder
    videos = list(Path("media/videos").rglob("*.mp4"))
    if not videos:
        print("⚠️ No video file found.")
        return None

    latest_video = max(videos, key=os.path.getmtime)
    saved_path = Path(output_dir) / latest_video.name
    latest_video.rename(saved_path)
    print(f"✅ Video saved to: {saved_path}")

    return str(saved_path)



def generate_voiceover_from_manim_code(manim_code: str, output_dir="outputs", filename="voiceover.mp3"):
    """
    Generates a spoken narration for a Manim script and saves it as an MP3 file.
    """
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    os.makedirs(output_dir, exist_ok=True)

    # Step 1 — create narration text
    prompt = f"""
    You are an educational narrator. Based on the following Manim Python code, 
    write a clear, very concise spoken explanation (the manim animations will do most of the explaining) that could accompany 
    the animation for a math learner. Make it sound like a teacher explaining a concept. 
    Get the timing correct in what you're saying and make the voiceover the same duration (roughly) as the video.

    Be sure to only include the actual spoken content and not any other text that isn't meant to actually be said.

    Manim Code:
    ```
    {manim_code}
    ```
    """

    print("🧠 Generating narration text...")
    narration_response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200,
    )

    narration_text = narration_response.choices[0].message.content.strip()
    print(f"🗣️ Narration text: {narration_text}")

    # Step 2 — generate TTS audio
    output_path = os.path.join(output_dir, filename)

    print("🎧 Generating voiceover MP3...")
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",  # You can change to "verse", "sage", etc.
        input=narration_text,
    ) as response:
        response.stream_to_file(output_path)

    print(f"✅ Saved voiceover: {output_path}")
    return output_path




def pipeline(user_query):
    # keywords = get_keywords(user_query)
    start_time = time.perf_counter()
    response = generate_manim_code(user_query)
    end_time = time.perf_counter()

    print("ELAPSED TIME GENERATION:" + str(end_time - start_time))

    manim_code = get_python_code(response)
    manim_command = get_manim_command(response)

    start_time = time.perf_counter()
    video_path = generate_manim_video(manim_code, manim_command)
    end_time = time.perf_counter()

    print("ELAPSED TIME GENERATION:" + str(end_time - start_time))


    voiceover_file = generate_voiceover_from_manim_code(manim_code)

    return video_path, voiceover_file




def main():

    prompt_input = input("What do you need help with?: ")
    pipeline(prompt_input)



if __name__ == "__main__":
    main()
    

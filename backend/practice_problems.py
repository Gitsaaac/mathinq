import openai
import os
import re
import matplotlib

# Use non-interactive backend (safe for server)
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import tempfile

client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def format_practice_problems_prompt(user_query: str) -> str:
    return f"""You are a LLM made for education and your job is to suggest a practice problem based on the user query.
Respond with a practice problem in LaTeX as well as the answer to the practice problem (also in LaTeX). Here is an example of a good query–response pair.
    
USER QUERY:
I need help with understanding systems of linear equations.

RESPONSE:
{{PROBLEM}}
Solve the following system:

$\\newline x + 2y = 3$
$\\newline 3x - 4y = -1$
{{PROBLEM}}

{{ANSWER}}
$\\newline x = 1, y = 1$
{{ANSWER}}

Please include the brackets with PROBLEM and ANSWER in your response (they should wrap the problem and answer). Return nothing but the PROBLEM tags, the LaTeX problem code, the ANSWER tags,
and the LaTeX answer code.

Here is the user query:

{user_query}
"""


def get_practice_problem(user_query: str) -> str:
    """Call the model and return raw text containing {{PROBLEM}} and {{ANSWER}} sections."""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "user", "content": format_practice_problems_prompt(user_query)}
        ],
        max_tokens=150,
        temperature=0.3,
    )
    return response.choices[0].message.content


def extract_problem(text: str) -> str | None:
    """
    Extracts the content inside {{PROBLEM}} ... {{PROBLEM}}.
    Returns the stripped text or None if not found.
    """
    pattern = r"\{PROBLEM\}(.*?)\{PROBLEM\}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_answer(text: str) -> str | None:
    """
    Extracts the content inside {{ANSWER}} ... {{ANSWER}}.
    Returns the stripped text or None if not found.
    """
    pattern = r"\{ANSWER\}(.*?)\{ANSWER\}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _clean_latex_for_mathtext(expr: str) -> tuple[str, bool]:
    """
    Make the LaTeX expression friendlier to matplotlib's mathtext:
    - Remember if it *looks like* a pure math wrapper ($...$, $$...$$, \[...\], \(...\)).
    - Strip outer wrappers if they exist.
    - Replace \newline with \\ for line breaks.

    Returns (cleaned_expr, had_math_wrapper_flag).
    """
    expr = expr.strip()
    had_math_wrapper = False

    # Detect and strip $$...$$
    if expr.startswith("$$") and expr.endswith("$$"):
        expr = expr[2:-2].strip()
        had_math_wrapper = True

    # Detect and strip $...$
    elif expr.startswith("$") and expr.endswith("$"):
        expr = expr[1:-1].strip()
        had_math_wrapper = True

    # Detect and strip \[ ... \]
    if expr.startswith(r"\[") and expr.endswith(r"\]"):
        expr = expr[2:-2].strip()
        had_math_wrapper = True

    # Detect and strip \( ... \)
    if expr.startswith(r"\(") and expr.endswith(r"\)"):
        expr = expr[2:-2].strip()
        had_math_wrapper = True

    # Convert \newline to \\ for line breaks
    expr = expr.replace(r"\newline", r"\\")
    return expr, had_math_wrapper


def latex_to_image_matplotlib(latex_expression: str, filename: str | None = None) -> str:
    """
    Renders LaTeX-ish text to a PNG file and returns the file path.
    Uses matplotlib's internal mathtext (no external LaTeX engine).
    """
    if filename is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        filename = tmp.name
        tmp.close()

    # ✅ Use internal mathtext, avoid external LaTeX / MiKTeX
    plt.rc("text", usetex=False)
    plt.rc("font", family="serif")

    cleaned, had_math_wrapper = _clean_latex_for_mathtext(latex_expression)

    # If it was pure math like "$x^2+1$", make sure we still wrap it in $...$
    # so mathtext kicks in. If there are already any $ inside, leave as-is.
    text_to_render = cleaned
    if had_math_wrapper and "$" not in cleaned:
        text_to_render = f"${cleaned}$"

    fig = plt.figure(figsize=(4, 1.2))
    fig.text(
        0.5,
        0.5,
        text_to_render,
        fontsize=22,
        ha="center",
        va="center",
        color="white"
    )

    plt.axis("off")
    plt.savefig(
        filename,
        dpi=300,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close(fig)

    return filename


def render_problem(problem_and_answer: str) -> str:
    """
    Extract the {{PROBLEM}} section and render it as a PNG.
    Returns the PNG file path.
    """
    problem = extract_problem(problem_and_answer)
    if not problem:
        raise ValueError("No {{PROBLEM}} section found.")
    latex = problem.strip()
    return latex_to_image_matplotlib(latex)


def render_answer(problem_and_answer: str) -> str:
    """
    Extract the {{ANSWER}} section and render it as a PNG.
    Returns the PNG file path.
    """
    answer = extract_answer(problem_and_answer)
    if not answer:
        raise ValueError("No {{ANSWER}} section found.")
    latex = answer.strip()
    return latex_to_image_matplotlib(latex)


def prob_ans_pipeline(user_query: str) -> tuple[str, str]:
    """
    Given a user_query string, generate a practice problem + answer,
    render both to PNG, and return (problem_png_path, answer_png_path).
    """
    prob_ans = get_practice_problem(user_query)
    prob_png = render_problem(prob_ans)
    ans_png = render_answer(prob_ans)
    return prob_png, ans_png

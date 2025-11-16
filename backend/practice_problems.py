import openai
import os
import re
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def format_practice_problems_prompt(user_query):
    return f"""You are a LLM made for education and your job is to suggest a practice problem based on the user query.
     Respond with an practice problem in latex as well as the answer to the practice problem (also in latex). Here is an example of a good query response pair.
    
    USER QUERY:
    I need help with understanding systems of linear equations.

    RESPONSE:
    {{PROBLEM}}
    Solve the following system:

$\newline x + 2y = 3$
$\newline 3x - 4y = -1$
    {{PROBLEM}}

    {{ANSWER}}
    $\newline x = 1, y = 1$
    {{ANSWER}}


    Please include the brackets with PROBLEM and ANSWER in your response (they should wrap the problem and answer). Return nothing but the PROBLEM tags, the latex problem code, the ANSWER tags,
    and the latex answer code.

    Here is the user query:

    {user_query}
    """

def get_practice_problem(user_query):
    response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "user", "content": format_practice_problems_prompt(user_query)}
    ],
    max_tokens=75)
    return response.choices[0].message.content


def extract_problem(text: str) -> str:
    """
    Extracts the content inside {{PROBLEM}} ... {{PROBLEM}}.
    Returns the stripped text or None if not found.
    """
    pattern = r"\{\{PROBLEM\}\}(.*?)\{\{PROBLEM\}\}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_answer(text: str) -> str:
    """
    Extracts the content inside {{ANSWER}} ... {{ANSWER}}.
    Returns the stripped text or None if not found.
    """
    pattern = r"\{\{ANSWER\}\}(.*?)\{\{ANSWER\}\}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def latex_to_image_matplotlib(latex_expression: str, filename: str = None) -> str:
    """
    Renders LaTeX to a PNG file and returns the file path.
    Uses Agg backend (server safe) and generates a temp file if no filename is given.
    """
    if filename is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        filename = tmp.name
        tmp.close()

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    fig = plt.figure(figsize=(4, 1.2))
    fig.text(0.5, 0.5, latex_expression, fontsize=22, ha='center', va='center')
    
    plt.axis("off")
    plt.savefig(filename, dpi=300, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    return filename

def render_problem(problem_and_answer):
    problem = extract_problem(problem_and_answer)
    if not problem:
        raise ValueError("No {{PROBLEM}} section found.")
    latex = problem.strip()
    return latex_to_image_matplotlib(latex)



def render_answer(problem_and_answer):
    answer = extract_answer(problem_and_answer)
    if not answer:
        raise ValueError("No {{ANSWER}} section found.")
    latex = answer.strip()
    return latex_to_image_matplotlib(latex)

def prob_ans_pipeline(user_query):
    prob_ans = get_practice_problem(user_query)
    prob_png = render_problem(prob_ans)
    ans_png = render_answer(prob_ans)

    return prob_png, ans_png
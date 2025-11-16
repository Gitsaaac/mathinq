# manim_examples.py

# Put each example here as a dict.
# "user"  = your question / problem
# "code"  = the Manim CE code you want as the answer

# These are examples of very good code generations given a prompt. These examples avoid many of the common pitfalls of generated
# manim code and renderings (no overlaps, no clipped symbols, mathematical correctness)

EXAMPLES = [
    {
        "user": "I need help with systems of linear equations.",
        "code": """
from manim import *

class LayoutManager:
   def __init__(self, scene, margin_ratio=0.07):
       self.scene = scene
       self.margin_ratio = margin_ratio


       fw = scene.camera.frame_width
       fh = scene.camera.frame_height
      
       self.left   = -fw/2  + fw*margin_ratio
       self.right  =  fw/2  - fw*margin_ratio
       self.top    =  fh/2  - fh*margin_ratio
       self.bottom = -fh/2  + fh*margin_ratio


   # Pull object inside safe zone
   def _pull_inside(self, mobj):
       xmin, xmax = mobj.get_left()[0], mobj.get_right()[0]
       ymin, ymax = mobj.get_bottom()[1], mobj.get_top()[1]


       dx = 0
       dy = 0


       if xmin < self.left:
           dx = self.left - xmin
       if xmax > self.right:
           dx = self.right - xmax
       if ymin < self.bottom:
           dy = self.bottom - ymin
       if ymax > self.top:
           dy = self.top - ymax


       mobj.shift([dx, dy, 0])
       return mobj


   # Autoscale to safe width ratio
   def autoscale(self, mobj, max_ratio=0.40):
       fw = self.scene.camera.frame_width
       if mobj.width > fw * max_ratio:
           mobj.scale_to_fit_width(fw * max_ratio)
       return mobj


   # Helper placement functions
   def place_top_left(self, mobj):
       mobj.to_corner(UL)
       return self._pull_inside(mobj)


   def place_top_right(self, mobj):
       mobj.to_corner(UR)
       return self._pull_inside(mobj)


   def place_bottom_left(self, mobj):
       mobj.to_corner(DL)
       return self._pull_inside(mobj)


   def place_bottom_right(self, mobj):
       mobj.to_corner(DR)
       return self._pull_inside(mobj)


   def place_center(self, mobj):
       mobj.move_to(ORIGIN)
       return self._pull_inside(mobj)


# ============================================================
# MAIN SCENE — Systems of Linear Equations
# ============================================================

class SystemsOfLinearEquations(Scene):
   def construct(self):


       layout = LayoutManager(self)


       # --- Title ---------------------------------------------------------
       title = Text("Systems of Linear Equations", weight=BOLD)
       layout.autoscale(title, max_ratio=0.60)
       layout.place_top_left(title)


       self.play(FadeIn(title))
       self.wait(0.3)


       # --- Explanation Text ----------------------------------------------
       explanation = Text(
           "A system of linear equations is a set of two or more\n"
           "lines whose intersection represents the solution.",
           font_size=32,
           line_spacing=0.75,
       )
       layout.autoscale(explanation, max_ratio=0.55)
       layout.place_bottom_left(explanation)


       self.play(FadeIn(explanation))
       self.wait(0.5)


       # --- Axes -----------------------------------------------------------
       axes = Axes(
           x_range=[-5, 5, 1],
           y_range=[-5, 5, 1],
           x_length=5,
           y_length=5,
           axis_config={"include_numbers": True},
       )
       axes.to_edge(RIGHT).shift(DOWN * 0.3)
       layout._pull_inside(axes)


       self.play(Create(axes))
       self.wait(0.3)


       # --- Lines ----------------------------------------------------------
       line1 = axes.plot(lambda x: 0.5 * x + 1, color=BLUE)
       line2 = axes.plot(lambda x: -1 * x + 3, color=RED)


       self.play(Create(line1), Create(line2))
       self.wait(0.4)


       # --- Line Equation Labels ------------------------------------------
       eq1 = MathTex("y = 0.5x + 1", color=BLUE)
       eq2 = MathTex("y = -x + 3", color=RED)


       eq_group = VGroup(eq1, eq2).arrange(DOWN, aligned_edge=LEFT, buff=0.3)


       layout.autoscale(eq_group, max_ratio=0.35)
       layout.place_top_right(eq_group)


       self.play(FadeIn(eq_group))
       self.wait(0.4)


       # --- Intersection Point --------------------------------------------
       intersection_point = axes.c2p(1.3333, 1.6667)
       dot = Dot(intersection_point, color=YELLOW)
       dot_label = MathTex(r"(1.33,\ 1.67)", color=YELLOW).next_to(dot, UP * 0.3)


       layout.autoscale(dot_label, max_ratio=0.25)
       layout._pull_inside(dot_label)


       self.play(FadeIn(dot), FadeIn(dot_label))
       self.wait(2)
"""

    },

    {
        "user": "I don't understand the quadratic formula",
        "code": """
from manim import *


# ============================================================
# CLEAN, SAFE LAYOUT MANAGER (reduced overlap version)
# ============================================================


class LayoutManager:
   def __init__(self, scene, margin_ratio=0.08):
       self.scene = scene
       fw = scene.camera.frame_width
       fh = scene.camera.frame_height


       self.margin_x = fw * margin_ratio
       self.margin_y = fh * margin_ratio


       self.left   = -fw/2  + self.margin_x
       self.right  =  fw/2  - self.margin_x
       self.top    =  fh/2  - self.margin_y
       self.bottom = -fh/2  + self.margin_y


   def autoscale(self, mobj, max_ratio=0.45):
       fw = self.scene.camera.frame_width
       if mobj.width > fw * max_ratio:
           mobj.scale_to_fit_width(fw * max_ratio)
       return mobj


   def safe_position(self, mobj, pos):
       mobj.move_to(pos)
       return self._pull_inside(mobj)


   def _pull_inside(self, mobj):
       xmin, xmax = mobj.get_left()[0], mobj.get_right()[0]
       ymin, ymax = mobj.get_bottom()[1], mobj.get_top()[1]


       dx = 0
       dy = 0


       if xmin < self.left:
           dx = self.left - xmin
       if xmax > self.right:
           dx = self.right - xmax
       if ymin < self.bottom:
           dy = self.bottom - ymin
       if ymax > self.top:
           dy = self.top - ymax


       mobj.shift([dx, dy, 0])
       return mobj




# ============================================================
# MAIN SCENE — clean, non-overlapping version
# ============================================================


class QuadraticFormulaScene(Scene):
   def construct(self):
       layout = LayoutManager(self)


       # --------------------------------------------------------
       # Title (centered at the top)
       # --------------------------------------------------------
       title = Text("Understanding the Quadratic Formula", weight=BOLD)
       layout.autoscale(title)
       layout.safe_position(title, UP * 3)


       self.play(FadeIn(title))
       self.wait(0.5)


       # --------------------------------------------------------
       # Intro block (left side)
       # --------------------------------------------------------
       intro_lines = VGroup(
           Text("A quadratic equation has the form:", font_size=32),
           MathTex("ax^2 + bx + c = 0").scale(1.0)
       ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)


       layout.autoscale(intro_lines)
       layout.safe_position(intro_lines, UP * 1.2 + LEFT * 3.5)


       self.play(FadeIn(intro_lines))
       self.wait(0.5)


       # --------------------------------------------------------
       # Quadratic formula block (right side)
       # --------------------------------------------------------
       formula = MathTex(
           rx = \frac\{-b \pm \sqrt{b^2 - 4ac}}{2a}, color=YELLOW)
       layout.autoscale(formula)
       layout.safe_position(formula, UP * 1.2 + RIGHT * 3.3)


       self.play(Write(formula))
       self.wait(0.6)


       explanation = Text(
           "The quadratic formula gives the x-values\n"
           "where the graph crosses the x-axis.",
           font_size=30,
           line_spacing=0.8
       )
       layout.autoscale(explanation)
       layout.safe_position(explanation, DOWN * 2.4 + LEFT * 3.5)


       self.play(FadeIn(explanation))
       self.wait(0.6)


       # --------------------------------------------------------
       # Draw the axes (bottom-right)
       # --------------------------------------------------------
       axes = Axes(
           x_range=[-1, 6, 1],
           y_range=[-2, 6, 1],
           x_length=5,
           y_length=3.5,
           axis_config={"include_numbers": True},
       )


       layout.safe_position(axes, DOWN * 1.8 + RIGHT * 2.8)


       self.play(Create(axes))
       self.wait(0.3)


       # --------------------------------------------------------
       # Example parabola: y = x^2 - 4x + 3
       # --------------------------------------------------------
       parabola = axes.plot(lambda x: x**2 - 4*x + 3, color=BLUE)
       self.play(Create(parabola))
       self.wait(0.4)


       # --------------------------------------------------------
       # Mark the roots visually
       # --------------------------------------------------------
       root1 = axes.c2p(1, 0)
       root2 = axes.c2p(3, 0)


       d1 = Dot(root1, color=RED)
       d2 = Dot(root2, color=RED)


       l1 = MathTex("x=1", color=RED).scale(0.6).next_to(d1, DOWN * 0.3)
       l2 = MathTex("x=3", color=RED).scale(0.6).next_to(d2, DOWN * 0.3)


       layout.autoscale(l1, max_ratio=0.18)
       layout.autoscale(l2, max_ratio=0.18)


       layout._pull_inside(l1)
       layout._pull_inside(l2)


       self.play(FadeIn(d1), FadeIn(d2), FadeIn(l1), FadeIn(l2))
       self.wait(0.5)


       # --------------------------------------------------------
       # Final conclusion (center)
       # --------------------------------------------------------
       final_note = Text(
           "The quadratic formula always finds the x-intercepts,\n"
           "even when factoring is difficult.",
           font_size=32,
           line_spacing=0.8
       )


       layout.autoscale(final_note)
       layout.safe_position(final_note, DOWN * 0.3)


       self.play(FadeIn(final_note))
       self.wait(2)
"""
    }
]
